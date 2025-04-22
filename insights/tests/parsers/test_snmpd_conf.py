import doctest
import pytest

from insights.core.exceptions import ParseException
from insights.parsers import snmpd_conf
from insights.parsers.snmpd_conf import SnmpdConf
from insights.tests import context_wrap


SNMPD_CONF = """
#       sec.name  source          community
com2sec notConfigUser  default       public

#       groupName      securityModel securityName
group   notConfigGroup v1           notConfigUser
group   notConfigGroup v2c           notConfigUser

# Make at least  snmpwalk -v 1 localhost -c public system fast again.
#       name           incl/excl     subtree         mask(optional)
view    systemview    included   .1.3.6.1.2.1.1
view    systemview    included   .1.3.6.1.2.1.25.1.1

#       group          context sec.model sec.level prefix read   write  notif
access  notConfigGroup ""      any       noauth    exact  systemview none none

dontLogTCPWrappersConnects yes
include_ifmib_iface_prefix eth enp1s0
""".strip()

SNMPD_CONF_EMPTY = """
""".strip()


def test_snmpd_conf():
    result = SnmpdConf(context_wrap(SNMPD_CONF))
    assert len(result) == 6
    assert 'com2sec' in result
    assert result['group'] == ['notConfigGroup v1           notConfigUser', 'notConfigGroup v2c           notConfigUser']
    assert result['include_ifmib_iface_prefix'] == ['eth enp1s0']


def test_snmpd_conf_empty():
    with pytest.raises(ParseException) as exc:
        SnmpdConf(context_wrap(SNMPD_CONF_EMPTY))
    assert str(exc.value) == "Empty Content"


def test_doc():
    env = {
        'snmpd_conf': SnmpdConf(context_wrap(SNMPD_CONF))
    }
    failed, total = doctest.testmod(snmpd_conf, globs=env)
    assert failed == 0
