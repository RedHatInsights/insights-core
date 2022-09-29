"""
Nginx Configurations
====================

This module includes the following parsers:

NginxConf - file ``/etc/nginx/nginx.conf`` and other Nginx configuration files
------------------------------------------------------------------------------

NginxConfPEG - file ``/etc/nginx/nginx.conf`` and other Nginx configuration files
---------------------------------------------------------------------------------

ContainerNginxConfPEG - file ``/etc/nginx/nginx.conf`` and other Nginx configuration files of running containers
----------------------------------------------------------------------------------------------------------------
"""
import string

from insights.contrib.nginxparser import create_parser, UnspacedList
from insights.core import ConfigParser, LegacyItemAccess, Parser, ContainerParser
from insights.core.plugins import parser
from insights.parsers import ParseException, get_active_lines
from insights.parsr import (EOF, EmptyQuotedString, Forward, LeftCurly, Lift, LineEnd, RightCurly,
                            Many, Number, OneLineComment, PosMarker, SemiColon, QuotedString,
                            skip_none, String, WS, WSChar)
from insights.parsr.query import Directive, Entry, Section
from insights.specs import Specs
from insights.util import deprecated


@parser(Specs.nginx_conf)
class NginxConf(Parser, LegacyItemAccess):
    """
    .. warning::
        This parser is deprecated, please import
        :py:class:`insights.combiners.nginx_conf.NginxConfTree` instead.

    Parse the keyword-and-value of a Nginx configuration file.

    Generally, each line is split on the first space into key and value, leading
    and trailing space being ignored.

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
        >>> type(nginxconf)
        <class 'insights.parsers.nginx_conf.NginxConf'>
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
    def __init__(self, *args, **kwargs):
        deprecated(NginxConf, "Import NginxConfTree from insights.combiners.nginx_conf instead.", "3.0.300")
        super(NginxConf, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        list_result = UnspacedList(create_parser().parseString("\n".join(get_active_lines(content))).asList())
        self.data = self._convert_nginx_list_to_dict(list_result)

    def _convert_nginx_list_to_dict(self, li):
        """
        After parsed by create_parser(), the result is a list, it is better to convert to dict for convenience.
        """

        def _list_depth_to_dict(self, li):
            """
            Function to convert list whose depth is tree to dict. Generally, the section name would be a dict key, and content
            embraced by brace would be value. In some sections, the first item is like ['location', '/'], in this case, the
            convert rule is that 'location' would be the key, and add {"name":'/'} key-value to the dict value.
            """
            dict_ret = {}
            if self._depth(li) == 1:
                return self._handle_key_value(dict_ret, li[0], li[1])
            else:
                for sub_item in li[1]:
                    tmp_dict = _list_depth_to_dict(self, sub_item)
                    tmp_key = list(tmp_dict.keys())[0]
                    tmp_val = tmp_dict[tmp_key]
                    tmp_val = tmp_val[0] if isinstance(tmp_val, list) else tmp_val
                    dict_ret.update(self._handle_key_value(dict_ret, tmp_key, tmp_val))
                if len(li[0]) > 1:
                    dict_ret["name"] = ' '.join(li[0][1:])
                return {li[0][0]: dict_ret}

        dict_all = {}
        for item in li:
            dict_all.update(_list_depth_to_dict(self, item))
        return dict_all

    def _handle_key_value(self, t_dict, key, value):
        """
        Function to handle dict key has multi value, and return the values as list.
        """
        # As it is possible that key "server", "location", "include"
        # and "upstream" have multi value, set the value of dict as list.
        if key in ("server", "location", "include", "upstream"):
            if key in t_dict:
                val = t_dict[key]
                val.append(value)
                return {key: val}
            return {key: [value]}
        else:
            return {key: value}

    def _depth(self, l):
        """
        Function to count the depth of a list
        """
        if isinstance(l, list) and len(l) > 0:
            return 1 + max(self._depth(item) for item in l)
        else:
            return 0


@parser(Specs.nginx_conf)
class NginxConfPEG(ConfigParser):
    """
    Parse the keyword-and-value of a Nginx configuration file.

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
        >>> type(nginxconfpeg)
        <class 'insights.parsers.nginx_conf.NginxConfPEG'>
        >>> nginxconfpeg['user'][-1].value
        'root'
        >>> nginxconfpeg['events']['worker_connections'][-1].value
        4096
        >>> nginxconfpeg['mail']['server'][0]['listen'][-1].value
        143
        >>> nginxconfpeg['http']['access_log'][-1].value
        'logs/access.log main'
        >>> nginxconfpeg['http']['server'][0]['location'][0]['fastcgi_pass'][-1].value
        '127.0.0.1:1025'
    """
    def __init__(self, *args, **kwargs):
        def to_entry(name, attrs, body):
            if body == ";":
                return Directive(name=name.value, attrs=attrs, lineno=name.lineno, src=self)
            return Section(name=name.value, attrs=attrs, children=body, lineno=name.lineno, src=self)

        name_chars = string.ascii_letters + "_/"
        Stmt = Forward()
        Num = Number & (WSChar | LineEnd | SemiColon)
        Comment = OneLineComment("#").map(lambda x: None)
        BeginBlock = WS >> LeftCurly << WS
        EndBlock = WS >> RightCurly << WS
        Bare = String(set(string.printable) - (set(string.whitespace) | set("#;{}'\"")))
        Name = WS >> PosMarker(String(name_chars) | EmptyQuotedString(name_chars)) << WS
        Attr = WS >> (Num | Bare | QuotedString) << WS
        Attrs = Many(Attr)
        Block = BeginBlock >> Many(Stmt).map(skip_none) << EndBlock
        Stanza = (Lift(to_entry) * Name * Attrs * (Block | SemiColon)) | Comment
        Stmt <= WS >> Stanza << WS
        Doc = Many(Stmt).map(skip_none)
        self.Top = Doc + EOF
        super(NginxConfPEG, self).__init__(*args, **kwargs)

    def parse_doc(self, content):
        try:
            return Entry(children=self.Top("\n".join(content))[0], src=self)
        except Exception:
            raise ParseException("There was an exception when parsing the config file.")


@parser(Specs.container_nginx_conf)
class ContainerNginxConfPEG(ContainerParser, NginxConfPEG):
    """
    Parser for the Nginx configuration files of running container.
    """
    pass
