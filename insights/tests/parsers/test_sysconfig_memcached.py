from insights.parsers.sysconfig import MemcachedSysconfig
from insights.tests import context_wrap

MEMCACHED_CONFIG = """
PORT="11211"
USER="memcached"
# max connection 2048
MAXCONN="2048"
# set ram size to 2048 - 2GiB
CACHESIZE="4096"
# disable UDP and listen to loopback ip 127.0.0.1, for network connection use real ip e.g., 10.0.0.5
OPTIONS="-U 0 -l 127.0.0.1"
""".strip()


def test_sysconfig_memcached():
    context = context_wrap(MEMCACHED_CONFIG, 'etc/sysconfig/memcached')
    conf = MemcachedSysconfig(context)

    assert 'OPTIONS' in conf
    assert 'FOO' not in conf
    assert conf.get('OPTIONS') == '-U 0 -l 127.0.0.1'
    assert conf.get('USER') == 'memcached'
