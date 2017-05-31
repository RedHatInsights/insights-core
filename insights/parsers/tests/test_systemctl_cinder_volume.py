from insights.parsers.systemctl_show import SystemctlShowCinderVolume
from insights.tests import context_wrap


SYSTEMCTL_SHOW_CINDER_VOLUME = """
UMask=0022
LimitCPU=18446744073709551615
LimitCORE=
LimitRSS=18446744073709551615
LimitNOFILE=4096
"""


def test_systemctl_show_cinder_volume():
    context = context_wrap(SYSTEMCTL_SHOW_CINDER_VOLUME)
    result = SystemctlShowCinderVolume(context).data
    assert result["LimitNOFILE"] == "4096"
    assert len(result) == 4
