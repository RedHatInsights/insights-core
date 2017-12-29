"""
NginxConf - nginx configuration files
=====================================
Parse the keyword-and-value of an Nginx configuration
file.

Generally, each line is split on the first space into
key and value, leading and trailing space being ignored.

Example nginx.conf file::

    user       root
    worker_processes  5;
    error_log  logs/error.log;
    pid        logs/nginx.pid;
    worker_rlimit_nofile 8192;

    events {
      worker_connections  4096;
    }

    mail {
      server_name mail.example.com;
      auth_http  localhost:9000/cgi-bin/auth;
      server {
        listen   143;
        protocol imap;
      }
    }

    http {
      include  /etc/nginx/conf.d/*.conf
      index    index.html index.htm index.php;

      default_type application/octet-stream;
      log_format   main '$remote_addr - $remote_user [$time_local]  $status '
                        '"$request" $body_bytes_sent "$http_referer" '
                        '"$http_user_agent" "$http_x_forwarded_for"';
      access_log   logs/access.log  main;
      sendfile     on;
      tcp_nopush   on;
      server_names_hash_bucket_size 128;

      server { # php/fastcgi
        listen       80;
        server_name  domain1.com www.domain1.com;
        access_log   logs/domain1.access.log  main;
        root         html;

        location ~ \.php$ {
          fastcgi_pass   127.0.0.1:1025;
        }
      }

      server { # simple reverse-proxy
        listen       80;
        server_name  domain2.com www.domain2.com;
        access_log   logs/domain2.access.log  main;

        location ~ ^/(images|javascript|js|css|flash|media|static)/  {
          root    /var/www/virtual/big.server.com/htdocs;
          expires 30d;
        }

        location / {
          proxy_pass   http://127.0.0.1:8080;
        }
      }

      map $http_upgrade $connection_upgrade {
        default upgrade;
        '' close;
      }

      upstream websocket {
        server 10.66.208.205:8010;
      }

      upstream big_server_com {
        server 127.0.0.3:8000 weight=5;
        server 127.0.0.3:8001 weight=5;
        server 192.168.0.1:8000;
        server 192.168.0.1:8001;
      }

      server { # simple load balancing
        listen          80;
        server_name     big.server.com;
        access_log      logs/big.server.access.log main;

        location / {
          proxy_pass      http://big_server_com;
        }
      }
    }

Examples:

    >>> nginxconf = shared[NginxConf]
    >>> nginxconf['user']
    'root'
    >>> nginxconf['events']['worker_connections'] # Values are all kept as strings.
    '4096'
    >>> nginxconf['mail']['server'][0]['listen']
    '143'
    >>> nginxconf['http']['access_log']
    'logs/access.log  main'
    >>> nginxconf['http']['server'][0]['location'][0]['fastcgi_pass']
    '127.0.0.1:1025'
"""
import string
import copy
from .. import parser, LegacyItemAccess, Parser, get_active_lines
from insights.contrib.pyparsing import (
    Literal, White, Word, alphanums, CharsNotIn, Combine, Forward, Group,
    Optional, OneOrMore, ZeroOrMore, Regex, stringEnd, restOfLine)


def create_parser():
    """
    A class that parses nginx configuration with pyparsing

    The MIT License (MIT)

    Copyright (c) 2014 Fatih Erikli

    Permission is hereby granted, free of charge, to any person obtaining a copy of
    this software and associated documentation files (the "Software"), to deal in
    the Software without restriction, including without limitation the rights to
    use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
    the Software, and to permit persons to whom the Software is furnished to do so,
    subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
    FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
    COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
    IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
    CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
    """

    # constants
    space = Optional(White())
    nonspace = Regex(r"\S+")
    left_bracket = Literal("{").suppress()
    right_bracket = space.leaveWhitespace() + Literal("}").suppress()
    semicolon = Literal(";").suppress()
    key = Word(alphanums + "_/+-.")
    dollar_var = Combine(Literal('$') + Regex(r"[^\{\};,\s]+"))
    condition = Regex(r"\(.+\)")
    # Matches anything that is not a special character, and ${SHELL_VARS}, AND
    # any chars in single or double quotes
    # All of these COULD be upgraded to something like
    # https://stackoverflow.com/a/16130746
    dquoted = Regex(r'(\".*\")')
    squoted = Regex(r"(\'.*\')")
    nonspecial = Regex(r"[^\{\};,]")
    varsub = Regex(r"(\$\{\w+\})")
    # nonspecial nibbles one character at a time, but the other objects take
    # precedence.  We use ZeroOrMore to allow entries like "break ;" to be
    # parsed as assignments
    value = Combine(ZeroOrMore(dquoted | squoted | varsub | nonspecial))

    location = CharsNotIn("{};," + string.whitespace)
    # modifier for location uri [ = | ~ | ~* | ^~ ]
    modifier = Literal("=") | Literal("~*") | Literal("~") | Literal("^~")

    # rules
    comment = space + Literal('#') + restOfLine

    assignment = space + key + Optional(space + value, default=None) + semicolon
    location_statement = space + Optional(modifier) + Optional(space + location + space)
    if_statement = space + Literal("if") + space + condition + space
    charset_map_statement = space + Literal("charset_map") + space + value + space + value

    map_statement = space + Literal("map") + space + nonspace + space + dollar_var + space
    # This is NOT an accurate way to parse nginx map entries; it's almost
    # certainly too permissive and may be wrong in other ways, but it should
    # preserve things correctly in mmmmost or all cases.
    #
    #    - I can neither prove nor disprove that it is correct wrt all escaped
    #      semicolon situations
    # Addresses https://github.com/fatiherikli/nginxparser/issues/19
    map_pattern = Regex(r'".*"') | Regex(r"'.*'") | nonspace
    map_entry = space + map_pattern + space + value + space + semicolon
    map_block = Group(
        Group(map_statement).leaveWhitespace() +
        left_bracket +
        Group(ZeroOrMore(Group(comment | map_entry)) + space).leaveWhitespace() +
        right_bracket)

    block = Forward()

    # key could for instance be "server" or "http", or "location" (in which case
    # location_statement needs to have a non-empty location)

    block_begin = (Group(space + key + location_statement) ^
                   Group(if_statement) ^
                   Group(charset_map_statement)).leaveWhitespace()

    block_innards = Group(ZeroOrMore(Group(comment | assignment) | block | map_block) + space).leaveWhitespace()

    block << Group(block_begin + left_bracket + block_innards + right_bracket)

    script = OneOrMore(Group(comment | assignment) ^ block ^ map_block) + space + stringEnd
    return script.parseWithTabs().leaveWhitespace()


class UnspacedList(list):
    """After handling by create_parser(), there is white space existing in the list. Use this class to wrap a list
     [of lists], making any whitespace entries magically invisible"""

    def __init__(self, list_source):
        # ensure our argument is not a generator, and duplicate any sublists
        self.spaced = copy.deepcopy(list(list_source))
        self.dirty = False

        # Turn self into a version of the source list that has spaces removed
        # and all sub-lists also UnspacedList()ed
        list.__init__(self, list_source)
        for i, entry in reversed(list(enumerate(self))):
            if isinstance(entry, list):
                sublist = UnspacedList(entry)
                list.__setitem__(self, i, sublist)
                self.spaced[i] = sublist.spaced
            elif self._spacey(entry):
                list.__delitem__(self, i)

    def _spacey(self, x):
        return (isinstance(x, str) and x.isspace()) or x == ''


@parser('nginx_conf')
class NginxConf(Parser, LegacyItemAccess):
    """
    Class for ``nginx.conf`` and ``conf.d`` configuration files.

    Gerenally nginx.conf is writed as key-value format. It has a mail section and several sections,
    http, mail, events, etc. They are unique, and subsection server and location in http section could
    be duplicate, so the value of these subsections may be list.
    """

    def parse_content(self, content):
        list_result = UnspacedList(create_parser().parseString("\n".join(get_active_lines(content))).asList())
        self.data = self._convert_nginx_list_to_dict(list_result)

    def _convert_nginx_list_to_dict(self, li):
        """
        After parsed by create_parser(), the result is a list, it is better to convert to dict for convenience.
        """

        def _listdepth_three(self, li):
            """
            Function to convert list whose depth is tree to dict. Generally, the section name would be a dict key, and content
            embraced by brace would be value. In some sections, the first item is like ['location', '/'], in this case, the
            convert rule is that 'location' would be the key, and add {"name":'/'} key-value to the dict value.
            """
            dict_result = {}
            for sub_item in li[1]:
                dict_result[sub_item[0]] = self._handle_key_value(dict_result, sub_item[0], sub_item[1])
            if len(li[0]) > 1:
                dict_result["name"] = ' '.join(li[0][1:])
            return {li[0][0]: dict_result}

        def _listdepth_five(self, li):
            """
            Function to convert list whose depth is five to dict.
            """
            dict_result = {}
            for sub_item in li[1]:
                if self._depth(sub_item) == 1:
                    dict_result[sub_item[0]] = self._handle_key_value(dict_result, sub_item[0], sub_item[1])
                if self._depth(sub_item) == 3:
                    tmp_dict = _listdepth_three(self, sub_item)
                    tmp_key = tmp_dict.keys()[0]
                    dict_result[tmp_key] = self._handle_key_value(dict_result, tmp_key, tmp_dict[tmp_key])
            return {li[0][0]: dict_result}

        def _listdepth_seven(self, li):
            """
            Function to convert list whose depth is seven to dict.
            """
            dict_result = {}
            for sub_item in li[1]:
                if self._depth(sub_item) == 1:
                    dict_result[sub_item[0]] = self._handle_key_value(dict_result, sub_item[0], sub_item[1])
                if self._depth(sub_item) == 3:
                    tmp_dict = _listdepth_three(self, sub_item)
                    tmp_key = tmp_dict.keys()[0]
                    dict_result[tmp_key] = self._handle_key_value(dict_result, tmp_key, tmp_dict[tmp_key])
                if self._depth(sub_item) == 5:
                    tmp_dict = _listdepth_five(self, sub_item)
                    tmp_key = tmp_dict.keys()[0]
                    dict_result[tmp_key] = self._handle_key_value(dict_result, tmp_key, tmp_dict[tmp_key])
            return {li[0][0]: dict_result}

        dict_all = {}
        for item in li:
            if self._depth(item) == 1:
                dict_all[item[0]] = self._handle_key_value(dict_all, item[0], item[1])
            if self._depth(item) == 3:
                dict_all.update(_listdepth_three(self, item))
            if self._depth(item) == 5:
                dict_all.update(_listdepth_five(self, item))
            if self._depth(item) == 7:
                dict_all.update(_listdepth_seven(self, item))
        return dict_all

    def _handle_key_value(self, t_dict, key, value):
        """
        Function to handle dict key has multi value, and return the values as list.
        """
        # As it is possible that key "server", "location", "include" and "upstream" have multi value, set the value of dict as list.
        if "server" in key or "location" in key or "include" in key or "upstream" in key:
            if key in t_dict:
                val = t_dict[key]
                val.append(value)
                return val
            return [value]
        else:
            return value

    def _depth(self, l):
        """
        Function to count the depth of a list
        """
        if isinstance(l, list):
            return 1 + max(self._depth(item) for item in l)
        else:
            return 0
