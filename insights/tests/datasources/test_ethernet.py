import pytest

from insights.core.dr import SkipComponent
from insights.specs.datasources.ethernet import interfaces, LocalSpecs
from mock.mock import Mock

RELATIVE_PATH = "insights_commands/ethernet_interfaces"

IP_LINK = """
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000\\    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
2: enp1s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP mode DEFAULT group default qlen 1000\\    link/ether 52:54:00:13:14:b5 brd ff:ff:ff:ff:ff:ff
3: enp8s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP mode DEFAULT group default qlen 1000\\    link/ether 52:54:00:e5:11:d4 brd ff:ff:ff:ff:ff:ff
4: enp1s0.2@enp1s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default qlen 1000\\    link/ether 52:54:00:13:14:b5 brd ff:ff:ff:ff:ff:ff
5: ib0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 4092 qdisc mq state DOWN group default qlen 256\\    link/infiniband 00:01:02:03:fd:90:0:00:00:00:00:00:ef:0d:8b:02:01:d9:82:fd
"""

IP_LINK_BAD = ""

EXPECTED = ['enp1s0', 'enp8s0', 'enp1s0.2']


def test_ethernet_interfaces():
    ip_link_command = Mock()
    ip_link_command.content = IP_LINK.splitlines()
    broker = {LocalSpecs.ip_link: ip_link_command}
    result = interfaces(broker)
    assert result is not None
    assert isinstance(result, list)
    assert result == sorted(EXPECTED)


def test_ethernet_interfaces_bad():
    ip_link_command = Mock()
    ip_link_command.content = IP_LINK_BAD.splitlines()
    broker = {LocalSpecs.ip_link: ip_link_command}
    with pytest.raises(SkipComponent):
        interfaces(broker)
