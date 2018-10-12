from insights.configtree import first, last
from insights.combiners.nginx_conf import _NginxConf, NginxConfTree
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


PROXY_CONF = """
proxy_redirect          off;
proxy_set_header        Host            $host;
proxy_set_header        X-Real-IP       $remote_addr;
proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
client_max_body_size    10m;
client_body_buffer_size 128k;
proxy_connect_timeout   90;
proxy_send_timeout      90;
proxy_read_timeout      90;
proxy_buffers           32 4k;
""".strip()


NGINX_CONF_PATH = "/etc/nginx/nginx.conf"
NGINX_PROXY_PATH = "/etc/nginx/proxy.conf"


def test_nginx_conf_tree():
    nginx1 = _NginxConf(context_wrap(NGINXCONF, path=NGINX_CONF_PATH))
    nginx2 = _NginxConf(context_wrap(PROXY_CONF, path=NGINX_PROXY_PATH))
    result = NginxConfTree([nginx1, nginx2])

    assert result['user'][-1].value == 'root'
    assert result['events'][-1]['worker_connections'][-1].value == 4096
    assert result['mail'][-1]['server'][0]['listen'][-1].value == 143
    assert result['http'][-1]['access_log'][-1].value == 'logs/access.log main'
    assert result['http'][-1]['server'][0]['location'][0]['fastcgi_pass'][-1].value == '127.0.0.1:1025'
    print result

