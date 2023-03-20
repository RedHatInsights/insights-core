import pytest
import doctest
from insights.parsers.hostname import Hostname as HnF, HostnameShort as HnS, HostnameDefault as HnD
from insights.parsers.systemid import SystemID
from insights.combiners.hostname import Hostname
from insights.combiners import hostname
from insights.tests import context_wrap

HOSTNAME_FULL = "rhel7.example.com"
HOSTNAME_SHORT = "rhel7"
HOSTNAME_DEF = "rhel7"
SYSTEMID_PROFILE_NAME = '''
<?xml version="1.0"?>
<params>
<param>
<value><struct>
<member>
<name>username</name>
<value><string>testuser</string></value>
</member>
<member>
<name>profile_name</name>
<value><string>example_profile</string></value>
</member>
<member>
<name>system_id</name>
<value><string>ID-example</string></value>
</member>
<member>
<name>architecture</name>
<value><string>x86_64</string></value>
</member>
</struct></value>
</param>
</params>
'''.strip()
SYSTEMID_NO_PROFILE_NAME = '''
<?xml version="1.0"?>
<params>
<param>
<member>
<name>username</name>
<value><string>testuser</string></value>
</member>
<member>
<name>architecture</name>
<value><string>x86_64</string></value>
</member>
</param>
</params>
'''.strip()


def test_get_hostname():
    hnf = HnF(context_wrap(HOSTNAME_FULL))
    expected = (HOSTNAME_FULL, HOSTNAME_SHORT, 'example.com')
    result = Hostname(hnf, None, None, None)
    assert result.fqdn == expected[0]
    assert result.hostname == expected[1]
    assert result.domain == expected[2]

    hns = HnS(context_wrap(HOSTNAME_SHORT))
    expected = (HOSTNAME_SHORT, HOSTNAME_SHORT, '')
    result = Hostname(None, None, hns, None)
    assert result.fqdn == expected[0]
    assert result.hostname == expected[1]
    assert result.domain == expected[2]

    hnd = HnD(context_wrap(HOSTNAME_DEF))
    expected = (HOSTNAME_DEF, HOSTNAME_DEF, '')
    result = Hostname(None, hnd, None, None)
    assert result.fqdn == expected[0]
    assert result.hostname == expected[1]
    assert result.domain == expected[2]


def test_get_systemid_hostname():
    sid = SystemID(context_wrap(SYSTEMID_PROFILE_NAME))
    expected = ('example_profile', 'example_profile', '')
    result = Hostname(None, None, None, sid)
    assert result.fqdn == expected[0]
    assert result.hostname == expected[1]
    assert result.domain == expected[2]


def test_get_all_hostname():
    hnf = HnF(context_wrap(HOSTNAME_FULL))
    hns = HnS(context_wrap(HOSTNAME_SHORT))
    hnd = HnD(context_wrap(HOSTNAME_DEF))
    sid = SystemID(context_wrap(SYSTEMID_PROFILE_NAME))
    expected = (HOSTNAME_FULL, HOSTNAME_SHORT, 'example.com')
    result = Hostname(hnf, hnd, hns, sid)
    assert result.fqdn == expected[0]
    assert result.hostname == expected[1]
    assert result.domain == expected[2]


def test_hostname_raise():
    with pytest.raises(Exception):
        sid = SystemID(context_wrap(SYSTEMID_NO_PROFILE_NAME))
        Hostname(None, None, None, None, sid)


def test_hostname_doc():
    hnf = HnF(context_wrap(HOSTNAME_FULL))
    hns = HnS(context_wrap(HOSTNAME_SHORT))
    hnd = HnD(context_wrap(HOSTNAME_DEF))
    sid = SystemID(context_wrap(SYSTEMID_PROFILE_NAME))
    env = {
        'hostname': Hostname(hnf, hnd, hns, sid),
    }
    failed, total = doctest.testmod(hostname, globs=env)
    assert failed == 0
