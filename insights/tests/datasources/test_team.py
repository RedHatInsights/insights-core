import pytest

from insights.core.dr import SkipComponent
from insights.specs.datasources.team import team_filter
from insights.parsers.nmcli import NmcliConnShow
from insights.tests import context_wrap

RELATIVE_PATH = "insights_commands/ethernet_interfaces"

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

NMCLI_C_SHOW_EMPTY = ""


def test_team_filter_1():
    mmcli_c_show = NmcliConnShow(context_wrap(NMCLI_C_SHOW_OUTPUT_1))

    broker = {
        NmcliConnShow: mmcli_c_show
    }
    result = team_filter(broker)
    assert result is not None
    assert isinstance(result, list)
    assert result == sorted(['team0', 'team1'])


def test_team_filter_2():
    mmcli_c_show = NmcliConnShow(context_wrap(NMCLI_C_SHOW_OUTPUT_2))

    broker = {
        NmcliConnShow: mmcli_c_show
    }
    with pytest.raises(SkipComponent):
        team_filter(broker)


def test_ethernet_interfaces_bad():
    mmcli_c_show = NmcliConnShow(context_wrap(NMCLI_C_SHOW_EMPTY))

    broker = {
        NmcliConnShow: mmcli_c_show
    }
    with pytest.raises(SkipComponent):
        team_filter(broker)
