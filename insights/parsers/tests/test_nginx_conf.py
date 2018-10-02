from insights.parsers import nginx_conf
from insights.tests import context_wrap


NGINXCONF = """
user       root;
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
  include    conf/mime.types;
  include    /etc/nginx/proxy.conf;
  include    /etc/nginx/fastcgi.conf;
  index    index.html index.htm index.php;
  log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

  default_type application/octet-stream;
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
      location /inner/ {
         proxy_pass http://u2;
         limit_except GET {
             allow 192.168.2.0/32;
         }
      }
    }
  }
}
""".strip()


def test_nginxconfiguration():
    nginxconf = nginx_conf.NginxConf(context_wrap(NGINXCONF))
    assert nginxconf['user'] == 'root'
    assert nginxconf['events']['worker_connections'] == '4096'
    assert nginxconf['mail']['server'][0]['listen'] == '143'
    assert nginxconf['http']['access_log'] == 'logs/access.log  main'
    assert nginxconf['http']['server'][0]['location'][0]['fastcgi_pass'] == '127.0.0.1:1025'
    assert nginxconf['http']['server'][1]['location'][1]['name'] == '/'
    assert nginxconf['http']['upstream'][1]['name'] == 'big_server_com'
    assert nginxconf["http"]["include"][0] == 'conf/mime.types'
    assert nginxconf['http']['upstream'][1]['server'][0] == '127.0.0.3:8000 weight=5'
    assert nginxconf['http']['log_format'] == """main  '$remote_addr - $remote_user [$time_local] "$request" '
'$status $body_bytes_sent "$http_referer" '
'"$http_user_agent" "$http_x_forwarded_for"'"""
    assert nginxconf['http']['server'][2]['location'][0]['location'][0]['limit_except']['allow'] == '192.168.2.0/32'
