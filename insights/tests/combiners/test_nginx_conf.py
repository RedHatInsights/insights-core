import pytest

from insights.combiners.nginx_conf import NginxConfTree
from insights.parsers import SkipException
from insights.parsers.nginx_conf import NginxConfPEG
from insights.parsr.query import startswith
from insights.tests import context_wrap

# test files extended from
# https://www.nginx.com/resources/wiki/start/topics/examples/full/

NGINX_CONF = r"""
user       www www;  ## Default: nobody
worker_processes  5;  ## Default: 1
error_log  logs/error.log;
pid        logs/nginx.pid;
worker_rlimit_nofile 8192;

events {
  worker_connections  4096;  ## Default: 1024
}

http {
  include    conf/mime.types;
  include    /etc/nginx/proxy.conf;
  include    /etc/nginx/fastcgi.conf;
  index    index.html index.htm index.php;

  default_type application/octet-stream;
  log_format   main '$remote_addr - $remote_user [$time_local]  $status '
    '"$request" $body_bytes_sent "$http_referer" '
    '"$http_user_agent" "$http_x_forwarded_for"';
  access_log   logs/access.log  main;
  sendfile     on;
  tcp_nopush   on;
  server_names_hash_bucket_size 128; # this seems to be required for some vhosts

  server { # php/fastcgi
    listen       80;
    server_name  domain1.com www.domain1.com;
    access_log   logs/domain1.access.log  main;
    root         html;
    ssl_certificate "/etc/pki/nginx/server.crt";

    location ~ \.php$ {
      fastcgi_pass   127.0.0.1:1025;
    }
  }

  server { # simple reverse-proxy
    listen       80;
    server_name  domain2.com www.domain2.com;
    access_log   logs/domain2.access.log  main;

    # serve static files
    location ~ ^/(images|javascript|js|css|flash|media|static)/  {
      root    /var/www/virtual/big.server.com/htdocs;
      expires 30d;
    }

    # pass requests for dynamic content to rails/turbogears/zope, et al
    location / {
      proxy_pass      http://127.0.0.1:8080;
    }
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
""".strip()

MIME_TYPES = """
types {
  text/html                             html htm shtml;
  text/css                              css;
  text/xml                              xml rss;
  image/gif                             gif;
  image/jpeg                            jpeg jpg;
  application/x-javascript              js;
  text/plain                            txt;
  text/x-component                      htc;
  text/mathml                           mml;
  image/png                             png;
  image/x-icon                          ico;
  image/x-jng                           jng;
  image/vnd.wap.wbmp                    wbmp;
  application/java-archive              jar war ear;
  application/mac-binhex40              hqx;
  application/pdf                       pdf;
  application/x-cocoa                   cco;
  application/x-java-archive-diff       jardiff;
  application/x-java-jnlp-file          jnlp;
  application/x-makeself                run;
  application/x-perl                    pl pm;
  application/x-pilot                   prc pdb;
  application/x-rar-compressed          rar;
  application/x-redhat-package-manager  rpm;
  application/x-sea                     sea;
  application/x-shockwave-flash         swf;
  application/x-stuffit                 sit;
  application/x-tcl                     tcl tk;
  application/x-x509-ca-cert            der pem crt;
  application/x-xpinstall               xpi;
  application/zip                       zip;
  application/octet-stream              deb;
  application/octet-stream              bin exe dll;
  application/octet-stream              dmg;
  application/octet-stream              eot;
  application/octet-stream              iso img;
  application/octet-stream              msi msp msm;
  audio/mpeg                            mp3;
  audio/x-realaudio                     ra;
  video/mpeg                            mpeg mpg;
  video/quicktime                       mov;
  video/x-flv                           flv;
  video/x-msvideo                       avi;
  video/x-ms-wmv                        wmv;
  video/x-ms-asf                        asx asf;
  video/x-mng                           mng;
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

FASTCGI_CONF = """
fastcgi_param  SCRIPT_FILENAME    $document_root$fastcgi_script_name;
fastcgi_param  QUERY_STRING       $query_string;
fastcgi_param  REQUEST_METHOD     $request_method;
fastcgi_param  CONTENT_TYPE       $content_type;
fastcgi_param  CONTENT_LENGTH     $content_length;
fastcgi_param  SCRIPT_NAME        $fastcgi_script_name;
fastcgi_param  REQUEST_URI        $request_uri;
fastcgi_param  DOCUMENT_URI       $document_uri;
fastcgi_param  DOCUMENT_ROOT      $document_root;
fastcgi_param  SERVER_PROTOCOL    $server_protocol;
fastcgi_param  GATEWAY_INTERFACE  CGI/1.1;
fastcgi_param  SERVER_SOFTWARE    nginx/$nginx_version;
fastcgi_param  REMOTE_ADDR        $remote_addr;
fastcgi_param  REMOTE_PORT        $remote_port;
fastcgi_param  SERVER_ADDR        $server_addr;
fastcgi_param  SERVER_PORT        $server_port;
fastcgi_param  SERVER_NAME        $server_name;

fastcgi_index  index.php;

fastcgi_param  REDIRECT_STATUS    200;
""".strip()


def test_nginx_includes():
    nginx_conf = context_wrap(NGINX_CONF, path="/etc/nginx/nginx.conf")
    mime_types_conf = context_wrap(MIME_TYPES, path="/etc/nginx/conf/mime.types")
    proxy_conf = context_wrap(PROXY_CONF, path="/etc/nginx/proxy.conf")
    fastcgi_conf = context_wrap(FASTCGI_CONF, path="/etc/nginx/fastcgi.conf")

    # individual parsers
    main = NginxConfPEG(nginx_conf)
    mime_types = NginxConfPEG(mime_types_conf)
    proxy = NginxConfPEG(proxy_conf)
    fastcgi = NginxConfPEG(fastcgi_conf)

    # combine them
    nginx = NginxConfTree([main, mime_types, proxy, fastcgi])

    # test /etc/nginx/nginx.conf
    assert nginx["events"]["worker_connections"][0].value == 4096
    assert nginx["http"]["server"]["ssl_certificate"][0].value == "/etc/pki/nginx/server.crt"

    # test inclusion of conf/mime.types (note relative path)
    text = nginx["http"]["types"][startswith("text/")]
    assert len(text) == 6

    # test inclusion of /etc/nginx/proxy.conf
    assert nginx.find("proxy_send_timeout").value == 90

    # test inclusion of /etc/nginx/fastcgi.conf
    assert nginx.find("fastcgi_pass").value == "127.0.0.1:1025"
    actual = nginx.find(("fastcgi_param", "GATEWAY_INTERFACE"))[0].attrs
    expected = ["GATEWAY_INTERFACE", "CGI/1.1"]
    assert actual == expected


def test_nginx_recursive_includes():
    # the content for both of these is the same to cause recursive include
    nginx_conf = context_wrap(NGINX_CONF, path="/etc/nginx/nginx.conf")
    mime_types_conf = context_wrap(NGINX_CONF, path="/etc/nginx/conf/mime.types")

    main = NginxConfPEG(nginx_conf)
    mime_types = NginxConfPEG(mime_types_conf)

    with pytest.raises(Exception):
        NginxConfTree([main, mime_types])


def test_nginx_empty():
    nginx_conf = context_wrap('', path="/etc/nginx/nginx.conf")
    with pytest.raises(SkipException):
        assert NginxConfPEG(nginx_conf) is None
