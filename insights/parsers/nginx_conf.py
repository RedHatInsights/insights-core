"""
Nginx Configurations
====================

This module includes the following parsers:

NginxConfPEG - file ``/etc/nginx/nginx.conf`` and other Nginx configuration files
---------------------------------------------------------------------------------

ContainerNginxConfPEG - file ``/etc/nginx/nginx.conf`` and other Nginx configuration files of running containers
----------------------------------------------------------------------------------------------------------------
"""
import string

from insights.core import ConfigParser, ContainerParser
from insights.core.exceptions import ParseException
from insights.core.plugins import parser
from insights.parsr import (EOF, EmptyQuotedString, Forward, LeftCurly, Lift, LineEnd, RightCurly,
                            Many, Number, OneLineComment, PosMarker, SemiColon, QuotedString,
                            skip_none, String, WS, WSChar)
from insights.parsr.query import Directive, Entry, Section
from insights.specs import Specs


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
