from insights.parsers.sysconfig import MongodSysconfig
from insights.tests import context_wrap

SYSCONFIG_MONGOD = """
OPTIONS="--quiet -f /etc/mongod.conf"
OPTIONS_EMPTY=""
"""


def test_sysconfig_mongod():
    context = context_wrap(SYSCONFIG_MONGOD, 'etc/sysconfig/mongod')
    sysconf = MongodSysconfig(context)

    assert 'OPTIONS' in sysconf
    assert sysconf.get('OPTIONS') == '--quiet -f /etc/mongod.conf'
    assert sysconf.get('OPTIONS_EMPTY') == ''
    assert sysconf.get('not_exist') is None
