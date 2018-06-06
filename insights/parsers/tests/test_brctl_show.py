import pytest
from insights.parsers.brctl_show import BrctlShow
from insights.tests import context_wrap
from insights.parsers import brctl_show, ParseException


BRCTL_SHOW = """
bridge name     bridge id               STP enabled     interfaces
br0             8000.08002731ddfd       no              eth1
                                                        eth2
                                                        eth3
br1             8000.0800278cdb62       no              eth4
                                                        eth5
br2             8000.0800278cdb63       yes             eth6
docker0         8000.0242d4cf2112       no
""".strip()

BRCTL_SHOW_TAB = """
bridge name	bridge id		STP enabled	interfaces
br0		8000.2047478aa2e8	no		em1
							vnet0
							vnet1
virbr9		8000.525400263a23	yes		virbr9-nic
"""  # noqa: W191, E101

BRCTL_SHOW_NO_BRIDGES = """
bridge name     bridge id   STP enabled     interfaces

"""

BRCTL_SHOW_LESS_COLUMN = """
bridge name     bridge id

"""

BRCTL_SHOW_ERROR = """
/usr/sbin/brctl: file not found
""".strip()

BRCTL_SHOW_TIMEOUT = """
timeout: failed to run command `/usr/sbin/brctl':
""".strip()


def test_get_brctl_show():
    # the content is splitted with tab     # noqa: E101
    result1 = BrctlShow(context_wrap(BRCTL_SHOW_TAB)).group_by_iface
    assert result1["br0"] == {
                "bridge id": "8000.2047478aa2e8",
                "STP enabled": "no",
                "interfaces": ['em1', 'vnet0', 'vnet1']
            }

    # the content is split with space
    result = BrctlShow(context_wrap(BRCTL_SHOW)).group_by_iface
    assert len(result) == 4

    assert result["br0"] == {
                "bridge id": "8000.08002731ddfd",
                "STP enabled": "no",
                "interfaces": ['eth1', 'eth2', 'eth3']
            }
    assert result["br1"] == {
                "bridge id": "8000.0800278cdb62",
                "STP enabled": "no",
                "interfaces": ['eth4', 'eth5']
            }
    assert result["br2"] == {
                "bridge id": "8000.0800278cdb63",
                "STP enabled": "yes",
                "interfaces": ['eth6']
            }
    assert result["docker0"] == {
                "bridge id": "8000.0242d4cf2112",
                "STP enabled": "no"
            }

    # Test handling of system with no bridges
    with pytest.raises(ParseException) as e_info:
        brctl_show.BrctlShow(context_wrap(BRCTL_SHOW_ERROR))
    assert "Invalid Data Found" in str(e_info.value)

    # Test handling of error output
    with pytest.raises(ParseException) as e_info:
        brctl_show.BrctlShow(context_wrap(BRCTL_SHOW_LESS_COLUMN))
    assert "Invalid Data Found" in str(e_info.value)

    with pytest.raises(ParseException) as e_info:
        brctl_show.BrctlShow(context_wrap(BRCTL_SHOW_TIMEOUT))
    assert "Invalid Data Found" in str(e_info.value)
