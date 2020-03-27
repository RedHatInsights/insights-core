import doctest
import pytest
from insights.parsers import firewall_cmd
from insights.parsers.firewall_cmd import FirewallCmdListALLZones
from insights.tests import context_wrap
from insights.parsers import SkipException, ParseException
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
  source-ports:
  icmp-blocks:
  rich rules:


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
    with pytest.raises(SkipException):
        FirewallCmdListALLZones(context_wrap(FIREWALL_LIST_ZONES_1))
    with pytest.raises(ContentException):
        FirewallCmdListALLZones(context_wrap(FIREWALL_LIST_ZONES_2))
    with pytest.raises(ParseException):
        FirewallCmdListALLZones(context_wrap(FIREWALL_LIST_ZONES_4))


def test_firewall_info():
    zones = FirewallCmdListALLZones(context_wrap(FIREWALL_LIST_ZONES_3))
    assert 'trusted' not in zones.active_zones
    assert zones.zones['public']['services'] == 'dhcpv6-client ssh'
    assert zones.zones['public']['icmp-block-inversion'] == 'no'
    assert zones.zones['public']['rich rules'] == ''
    assert zones.zones['trusted']['services'] == ''
    assert zones.zones['trusted']['icmp-block-inversion'] == 'yes'
