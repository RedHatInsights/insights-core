from falafel.mappers.brctl_show import BrctlShow
from falafel.tests import context_wrap


BRCTL_SHOW = """
bridge name     bridge id               STP enabled     interfaces
br0             8000.08002731ddfd       no              eth1
                                                        eth2
                                                        eth3
br1             8000.0800278cdb62       no              eth4
                                                        eth5
br2             8000.0800278cdb63       yes             eth6
docker0         8000.0242d4cf2112       no
"""


def test_get_brctl_show():

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
