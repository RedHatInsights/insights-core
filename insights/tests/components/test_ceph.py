import pytest
from insights import SkipComponent
from insights.tests import context_wrap
from insights.parsers.ps import PsAuxcww
from insights.combiners.ps import Ps
from insights.components.ceph import IsCephMonitor

PsAuxcww_CEPH = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0  19356  1544 ?        Ss   May31   0:01 init
user2    20164  0.0  0.0 108472  1896 pts/5    Ss   10:10   0:00 bash
root     20357  0.0  0.0   9120   832 ?        Ss   10:09   0:00 dhclient
root     22673  0.6 10.7 1618556 840452 ?      Sl   11:38   1:31 ceph-mon
vdsm     27323 98.0 11.3  9120    987 ?        Ss   10.01   1:31 vdsm
""".strip()

PsAuxcww_NO_CEPH = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0  19356  1544 ?        Ss   May31   0:01 init
user2    20164  0.0  0.0 108472  1896 pts/5    Ss   10:10   0:00 bash
root     20357  0.0  0.0   9120   832 ?        Ss   10:09   0:00 dhclient
vdsm     27323 98.0 11.3  9120    987 ?        Ss   10.01   1:31 vdsm
""".strip()


def test_is_ceph_monitor():
    ps_auxcww = PsAuxcww(context_wrap(PsAuxcww_CEPH))
    ps = Ps(None, None, None, None, ps_auxcww, None, None)
    result = IsCephMonitor(ps)
    assert isinstance(result, IsCephMonitor)

    ps_auxcww = PsAuxcww(context_wrap(PsAuxcww_NO_CEPH))
    ps = Ps(None, None, None, None, ps_auxcww, None, None)
    with pytest.raises(SkipComponent):
        IsCephMonitor(ps)
