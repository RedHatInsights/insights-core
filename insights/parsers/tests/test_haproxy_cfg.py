from insights.core.context import OSP
from insights.parsers.haproxy_cfg import HaproxyCfg
from insights.tests import context_wrap

haproxy_osp = """
# This file managed by Puppet
global
  daemon
  group  haproxy
  maxconn  10000
  pidfile  /var/run/haproxy.pid
  user  haproxy

defaults
  log  127.0.0.1 local2 warning
  mode  tcp
  option  tcplog
  option  redispatch
  retries  3
  timeout  connect 5s
  timeout  client 30s
  timeout  server 30s

listen amqp
  bind 10.64.111.121:5672
  mode  tcp
  option  tcpka
  option  tcplog
  timeout  client 900m
  timeout  server 900m
  server lb-backend-ncerdlabdell397 10.64.111.11:5672  check inter 1s
  server lb-backend-ncerdlabdell400 10.64.111.12:5672  check inter 1s
  server lb-backend-ncerdlabdell401 10.64.111.13:5672  check inter 1s

listen ceilometer-api
  bind 10.64.111.94:8777
  bind 10.64.111.93:8777
  bind 10.64.111.92:8777
  mode  tcp
  option  tcplog
  server lb-backend-ncerdlabdell397 10.64.111.11:8777  check inter 1s
  server lb-backend-ncerdlabdell400 10.64.111.12:8777  check inter 1s
  server lb-backend-ncerdlabdell401 10.64.111.13:8777  check inter 1s

listen cinder-api
  bind 10.64.111.97:8776
  bind 10.64.111.96:8776
  bind 10.64.111.95:8776
  mode  tcp
  option  tcplog
  server lb-backend-ncerdlabdell397 10.64.111.11:8776  check inter 1s
  server lb-backend-ncerdlabdell400 10.64.111.12:8776  check inter 1s
  server lb-backend-ncerdlabdell401 10.64.111.13:8776  check inter 1s

listen galera
  bind 10.64.111.98:3306
  mode  tcp
  option  tcplog
  option  httpchk
  option  tcpka
  stick  on dst
  stick-table  type ip size 2
  timeout  client 90m
  timeout  server 90m
  server pcmk-ncerdlabdell397 10.64.111.11:3306  check inter 1s port 9200 on-marked-down shutdown-sessions
  server pcmk-ncerdlabdell400 10.64.111.12:3306  check inter 1s port 9200 on-marked-down shutdown-sessions
  server pcmk-ncerdlabdell401 10.64.111.13:3306  check inter 1s port 9200 on-marked-down shutdown-sessions

listen glance-api
  bind 10.64.111.101:9292
  bind 10.64.111.100:9292
  bind 10.64.111.99:9292
  mode  tcp
  option  tcplog
  server lb-backend-ncerdlabdell397 10.64.111.11:9292  check inter 1s
  server lb-backend-ncerdlabdell400 10.64.111.12:9292  check inter 1s
  server lb-backend-ncerdlabdell401 10.64.111.13:9292  check inter 1s

listen glance-registry
  bind 10.64.111.101:9191
  bind 10.64.111.100:9191
  bind 10.64.111.99:9191
  mode  tcp
  option  tcplog
  server lb-backend-ncerdlabdell397 10.64.111.11:9191  check inter 1s
  server lb-backend-ncerdlabdell400 10.64.111.12:9191  check inter 1s
  server lb-backend-ncerdlabdell401 10.64.111.13:9191  check inter 1s

listen heat-api
  bind 10.64.111.104:8004
  bind 10.64.111.103:8004
  bind 10.64.111.102:8004
  mode  tcp
  option  tcplog
  server lb-backend-ncerdlabdell397 10.64.111.11:8004  check inter 1s
  server lb-backend-ncerdlabdell400 10.64.111.12:8004  check inter 1s
  server lb-backend-ncerdlabdell401 10.64.111.13:8004  check inter 1s

listen heat-cfn
  bind 10.64.111.107:8000
  bind 10.64.111.106:8000
  bind 10.64.111.105:8000
  mode  tcp
  option  tcplog
  server lb-backend-ncerdlabdell397 10.64.111.11:8000  check inter 1s
  server lb-backend-ncerdlabdell400 10.64.111.12:8000  check inter 1s
  server lb-backend-ncerdlabdell401 10.64.111.13:8000  check inter 1s

listen heat-cloudwatch
  bind 10.64.111.103:8003
  bind 10.64.111.102:8003
  mode  tcp
  option  tcplog
  server lb-backend-ncerdlabdell397 10.64.111.11:8003  check inter 1s
  server lb-backend-ncerdlabdell400 10.64.111.12:8003  check inter 1s
  server lb-backend-ncerdlabdell401 10.64.111.13:8003  check inter 1s

listen horizon
  bind 10.64.111.110:80
  bind 10.64.111.109:80
  bind 10.64.111.108:80
  mode  http
  cookie  SERVERID insert indirect nocache
  option  httplog
  server lb-backend-ncerdlabdell397 10.64.111.11:80 cookie lb-backend-ncerdlabdell397 check inter 1s
  server lb-backend-ncerdlabdell400 10.64.111.12:80 cookie lb-backend-ncerdlabdell400 check inter 1s
  server lb-backend-ncerdlabdell401 10.64.111.13:80 cookie lb-backend-ncerdlabdell401 check inter 1s

listen keystone-admin
  bind 10.64.111.113:35357
  bind 10.64.111.112:35357
  bind 10.64.111.111:35357
  mode  tcp
  option  tcplog
  server lb-backend-ncerdlabdell397 10.64.111.11:35357  check inter 1s
  server lb-backend-ncerdlabdell400 10.64.111.12:35357  check inter 1s
  server lb-backend-ncerdlabdell401 10.64.111.13:35357  check inter 1s

listen keystone-public
  bind 10.64.111.113:5000
  bind 10.64.111.112:5000
  bind 10.64.111.111:5000
  mode  tcp
  option  tcplog
  server lb-backend-ncerdlabdell397 10.64.111.11:5000  check inter 1s
  server lb-backend-ncerdlabdell400 10.64.111.12:5000  check inter 1s
  server lb-backend-ncerdlabdell401 10.64.111.13:5000  check inter 1s

listen neutron-api
  bind 10.64.111.117:9696
  bind 10.64.111.116:9696
  bind 10.64.111.115:9696
  mode  tcp
  option  tcplog
  server lb-backend-ncerdlabdell397 10.64.111.11:9696  check inter 1s
  server lb-backend-ncerdlabdell400 10.64.111.12:9696  check inter 1s
  server lb-backend-ncerdlabdell401 10.64.111.13:9696  check inter 1s

listen nova-api
  bind 10.64.111.120:8774
  bind 10.64.111.119:8774
  bind 10.64.111.118:8774
  mode  tcp
  option  tcplog
  server lb-backend-ncerdlabdell397 10.64.111.11:8774  check inter 1s
  server lb-backend-ncerdlabdell400 10.64.111.12:8774  check inter 1s
  server lb-backend-ncerdlabdell401 10.64.111.13:8774  check inter 1s

listen nova-metadata
  bind 10.64.111.120:8775
  bind 10.64.111.119:8775
  bind 10.64.111.118:8775
  mode  tcp
  option  tcplog
  server lb-backend-ncerdlabdell397 10.64.111.11:8775  check
  server lb-backend-ncerdlabdell400 10.64.111.12:8775  check
  server lb-backend-ncerdlabdell401 10.64.111.13:8775  check

listen nova-novncproxy
  bind 10.64.111.120:6080
  bind 10.64.111.119:6080
  bind 10.64.111.118:6080
  mode  tcp
  option  tcplog
  server lb-backend-ncerdlabdell397 10.64.111.11:6080  check inter 1s
  server lb-backend-ncerdlabdell400 10.64.111.12:6080  check inter 1s
  server lb-backend-ncerdlabdell401 10.64.111.13:6080  check inter 1s

listen nova-xvpvncproxy
  bind 10.64.111.120:6081
  bind 10.64.111.119:6081
  bind 10.64.111.118:6081
  mode  tcp
  option  tcplog
  server lb-backend-ncerdlabdell397 10.64.111.11:6081  check inter 1s
  server lb-backend-ncerdlabdell400 10.64.111.12:6081  check inter 1s
  server lb-backend-ncerdlabdell401 10.64.111.13:6081  check inter 1s

listen stats
  bind *:81
  mode  http
  stats  enable
"""

haproxy_mysql = """

global
  daemon
  group  haproxy
  log  /dev/log local0
  maxconn  20480
  pidfile  /var/run/haproxy.pid
  user  haproxy

defaults
  log  global
  maxconn  4096
  mode  tcp
  retries  3
  timeout  http-request 10s
  timeout  queue 1m
  timeout  connect 10s
  timeout  client 1m
  timeout  server 1m
  timeout  check 10s


listen mysql
  bind 10.0.1.10:3306
  option tcpka
  option httpchk
  stick on dst
  stick-table type ip size 1000
  timeout client 0
  timeout server 0
  server chicago-controller-0 10.0.1.14:3306 backup check fall 5 inter 2000 on-marked-down shutdown-sessions port 9200 rise 2
  server chicago-controller-1 10.0.1.12:3306 backup check fall 5 inter 2000 on-marked-down shutdown-sessions port 9200 rise 2
  server chicago-controller-2 10.0.1.15:3306 backup check fall 5 inter 2000 on-marked-down shutdown-sessions port 9200 rise 2

"""
osp_c = OSP()
osp_c.role = "Controller"


def test_haproxy_cls_1():
    r = HaproxyCfg(context_wrap(haproxy_osp, osp=osp_c))
    assert r.data.get("global").get("maxconn") == "10000"
    assert r.data.get("listen galera").get("mode") == "tcp"
    assert r.lines[2] == "group  haproxy"


def test_haproxy_cls_2():
    result = HaproxyCfg(context_wrap(haproxy_mysql, osp=osp_c))
    assert "daemon" in result.data.get("global")
    assert "maxconn" in result.data.get("global")
    assert result.data.get("defaults").get("maxconn") == "4096"
    assert "queue 1m" in result.data.get("defaults").get("timeout")
