import doctest
import pytest
from insights.parsers import firewall_cmd
from insights.parsers.firewall_cmd import FirewallCmdListALLZones
from insights.tests import context_wrap
from insights.parsers import ParseException
from insights.core.plugins import ContentException

FIREWALL_LIST_ZONES_1 = """
FirewallD is not running
""".strip()

FIREWALL_LIST_ZONES_2 = """
-bash: firewall-cmd: command not found
""".strip()

FIREWALL_LIST_ZONES_3 = """
block
  target: %%REJECT%%
  icmp-block-inversion: no
  interfaces:
  sources:
  services:
  ports:
  protocols:
  masquerade: no
  forward-ports:
  source-ports:
  icmp-blocks:
  rich rules:


dmz
  target: default
  icmp-block-inversion: no
  interfaces:
  sources:
  services: ssh
  ports:
  protocols:
  masquerade: no
  forward-ports:
  source-ports:
  icmp-blocks:
  rich rules:


public (active, default)
  target: default
  icmp-block-inversion: no
  interfaces: eno1
  sources:
  services: dhcpv6-client ssh
  ports:
  protocols:
  masquerade: no
  forward-ports: port=80:proto=tcp:toport=12345:toaddr=
        port=81:proto=tcp:toport=1234:toaddr=
        port=83:proto=tcp:toport=456:toaddr=10.72.47.45
  source-ports:
  icmp-blocks:
  rich rules:
        rule family="ipv4" source address="10.0.0.0/24" destination address="192.168.0.10/32" port port="8080-8090" protocol="tcp" accept
        rule family="ipv4" source address="10.0.0.0/24" destination address="192.168.0.10/32" port port="443" protocol="tcp" reject
        rule family="ipv4" source address="192.168.0.10/24" reject
        rule family="ipv6" source address="1:2:3:4:6::" forward-port port="4011" protocol="tcp" to-port="4012" to-addr="1::2:3:4:7"


trusted
  target: ACCEPT
  icmp-block-inversion: yes
  interfaces:
  sources:
  services:
  ports:
  protocols:
  masquerade: no
  forward-ports:
  source-ports:
  icmp-blocks:
  rich rules:
""".strip()

FIREWALL_LIST_ZONES_4 = """
public (active)
    target: default
    icmp-block-inversion: no
    interfaces: eno1
    sources:
    services: dhcpv6-client ssh
    ports:
    protocols:
    masquerade: no
    forward-ports:
    source-ports
    icmp-blocks
    rich rules
""".strip()


def test_docs():
    env = {
        'zones': FirewallCmdListALLZones(context_wrap(FIREWALL_LIST_ZONES_3))
    }
    failed, total = doctest.testmod(firewall_cmd, globs=env)
    assert failed == 0


def test_empty_content():
    with pytest.raises(ContentException):
        FirewallCmdListALLZones(context_wrap(FIREWALL_LIST_ZONES_1))
    with pytest.raises(ContentException):
        FirewallCmdListALLZones(context_wrap(FIREWALL_LIST_ZONES_2))
    with pytest.raises(ParseException):
        FirewallCmdListALLZones(context_wrap(FIREWALL_LIST_ZONES_4))


def test_firewall_info():
    zones = FirewallCmdListALLZones(context_wrap(FIREWALL_LIST_ZONES_3))
    assert 'trusted' not in zones.active_zones
    assert zones.zones['public']['services'] == ['dhcpv6-client ssh']
    assert zones.zones['public']['icmp-block-inversion'] == ['no']
    assert zones.zones['trusted']['services'] == []
    assert zones.zones['trusted']['icmp-block-inversion'] == ['yes']
    zone_info = ['target', 'icmp-block-inversion', 'interfaces', 'sources', 'services',
                         'ports', 'protocols', 'masquerade', 'forward-ports', 'source-ports',
                         'icmp-blocks', 'rich rules']
    assert all(key in zones.zones['public'] for key in zone_info)
    assert 'port=80:proto=tcp:toport=12345:toaddr=' in zones.zones['public']['forward-ports']
    assert 'port=83:proto=tcp:toport=456:toaddr=10.72.47.45' in zones.zones['public']['forward-ports']
    assert len(zones.zones['public']['forward-ports']) == 3
    assert len(zones.zones['public']['rich rules']) == 4
    assert 'active' in zones.zones['public']['_attributes']
    assert 'default' in zones.zones['public']['_attributes']
    assert 'rule family="ipv4" source address="10.0.0.0/24" destination address="192.168.0.10/32" port port="8080-8090" protocol="tcp" accept' in zones.zones['public']['rich rules']
    assert 'rule family="ipv4" source address="192.168.0.10/24" reject' in zones.zones['public']['rich rules']
