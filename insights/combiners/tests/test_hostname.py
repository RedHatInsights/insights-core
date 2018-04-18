import pytest
from insights.parsers.hostname import Hostname
from insights.parsers.facter import Facter
from insights.parsers.systemid import SystemID
from insights.combiners.hostname import hostname
from insights.tests import context_wrap

HOSTNAME = "rhel7.example.com"
HOSTNAME_SHORT = "rhel7"
FACTS_FQDN = """
COMMAND> facter

architecture => x86_64
augeasversion => 1.1.0
facterversion => 1.7.6
filesystems => xfs
fqdn => ewa-satellite.example.com
hostname => ewa-satellite
""".strip()
FACTS_NO_FQDN = """
COMMAND> facter

architecture => x86_64
facterversion => 1.7.6
filesystems => xfs
""".strip()
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
    hn = Hostname(context_wrap(HOSTNAME))
    expected = (HOSTNAME, HOSTNAME_SHORT, 'example.com')
    result = hostname(hn, None, None)
    assert result.fqdn == expected[0]
    assert result.hostname == expected[1]
    assert result.domain == expected[2]

    hn = Hostname(context_wrap(HOSTNAME_SHORT))
    expected = (HOSTNAME_SHORT, HOSTNAME_SHORT, '')
    result = hostname(hn, None, None)
    assert result.fqdn == expected[0]
    assert result.hostname == expected[1]
    assert result.domain == expected[2]


def test_get_facter_hostname():
    hn = Facter(context_wrap(FACTS_FQDN))
    expected = ('ewa-satellite.example.com', 'ewa-satellite', 'example.com')
    result = hostname(None, hn, None)
    assert result.fqdn == expected[0]
    assert result.hostname == expected[1]
    assert result.domain == expected[2]


def test_get_systemid_hostname():
    hn = SystemID(context_wrap(SYSTEMID_PROFILE_NAME))
    expected = ('example_profile', 'example_profile', '')
    result = hostname(None, None, hn)
    assert result.fqdn == expected[0]
    assert result.hostname == expected[1]
    assert result.domain == expected[2]


def test_get_all_hostname():
    hn = Hostname(context_wrap(HOSTNAME))
    fhn = Facter(context_wrap(FACTS_FQDN))
    shn = SystemID(context_wrap(SYSTEMID_PROFILE_NAME))
    expected = (HOSTNAME, HOSTNAME_SHORT, 'example.com')
    result = hostname(hn, fhn, shn)
    assert result.fqdn == expected[0]
    assert result.hostname == expected[1]
    assert result.domain == expected[2]


def test_hostname_raise():
    with pytest.raises(Exception):
        hn = Hostname(context_wrap(""))
        hostname(hn, None, None)
