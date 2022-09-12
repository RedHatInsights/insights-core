import pytest

from insights.core.dr import SkipComponent
from insights.specs.datasources.ethernet import interfaces, LocalSpecs, team_interfaces
from insights.parsers.nmcli import NmcliConnShow
from mock.mock import Mock
from insights.tests import context_wrap

RELATIVE_PATH = "insights_commands/ethernet_interfaces"

IP_LINK = """
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000\\    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
2: enp1s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP mode DEFAULT group default qlen 1000\\    link/ether 52:54:00:13:14:b5 brd ff:ff:ff:ff:ff:ff
3: enp8s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP mode DEFAULT group default qlen 1000\\    link/ether 52:54:00:e5:11:d4 brd ff:ff:ff:ff:ff:ff
4: enp1s0.2@enp1s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default qlen 1000\\    link/ether 52:54:00:13:14:b5 brd ff:ff:ff:ff:ff:ff
5: ib0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 4092 qdisc mq state DOWN group default qlen 256\\    link/infiniband 00:01:02:03:fd:90:0:00:00:00:00:00:ef:0d:8b:02:01:d9:82:fd
"""

IP_LINK_BAD = ""

NMCLI_C_SHOW_OUTPUT_1 = """
NAME      UUID                                  TYPE      DEVICE
enp0s3    320d4923-c410-4b22-b7e9-afc5f794eecc  ethernet  enp0s3
virbr0    7c7dec66-4a8c-4b49-834a-889194b3b83c  bridge    virbr0
test-net  f858b1cc-d149-4de0-93bc-b1826256847a  ethernet  --
team0     bf000427-d9f1-432f-819d-257edb86c6fb  team      team0
ens3      1b1f5c95-1026-4699-95e5-2cd5baa033c3  ethernet  ens3
ens8      a2c39643-b356-435a-955c-50cef6b36052  ethernet  ens8
team1     ca07b1cf-b293-4871-b255-17f1abfa991d  team      team1
"""

NMCLI_C_SHOW_OUTPUT_2 = """
NAME      UUID                                  TYPE      DEVICE
enp0s3    320d4923-c410-4b22-b7e9-afc5f794eecc  ethernet  enp0s3
"""

NMCLI_C_SHOW_OUTPUT_3 = """
NAME      UUID                                  TYPE      DEVICE
team0     bf000427-d9f1-432f-819d-257edb86c6fb  team      --
"""

NMCLI_C_SHOW_EMPTY = """
NAME      UUID                                  TYPE      DEVICE
"""

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


def test_team_device_1():
    mmcli_c_show = NmcliConnShow(context_wrap(NMCLI_C_SHOW_OUTPUT_1))

    broker = {
        NmcliConnShow: mmcli_c_show
    }
    result = team_interfaces(broker)
    assert result is not None
    assert isinstance(result, list)
    assert result == sorted(['team0', 'team1'])


def test_team_device_2():
    mmcli_c_show = NmcliConnShow(context_wrap(NMCLI_C_SHOW_OUTPUT_2))

    broker = {
        NmcliConnShow: mmcli_c_show
    }
    with pytest.raises(SkipComponent):
        team_interfaces(broker)


def test_team_device_3():
    mmcli_c_show = NmcliConnShow(context_wrap(NMCLI_C_SHOW_OUTPUT_3))

    broker = {
        NmcliConnShow: mmcli_c_show
    }
    with pytest.raises(SkipComponent):
        team_interfaces(broker)


def test_team_device_bad():
    mmcli_c_show = NmcliConnShow(context_wrap(NMCLI_C_SHOW_EMPTY))

    broker = {
        NmcliConnShow: mmcli_c_show
    }
    with pytest.raises(SkipComponent):
        team_interfaces(broker)
