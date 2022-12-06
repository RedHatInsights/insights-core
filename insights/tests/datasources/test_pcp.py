import datetime
import pytest

from mock.mock import patch

from insights.combiners.ps import Ps
from insights.combiners.services import Services
from insights.core import dr
from insights.core.exceptions import SkipComponent
from insights.parsers.ps import PsAuxcww
from insights.parsers.ros_config import RosConfig
from insights.parsers.systemd.unitfiles import UnitFiles
from insights.specs.datasources.pcp import pcp_enabled, pmlog_summary_args
from insights.tests import context_wrap

PS_AUXCWW = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0  19356  1544 ?        Ss   May31   0:01 init
root      1821  0.0  0.0      0     0 ?        S    May31   0:29 kondemand/0
root     20357  0.0  0.0   9120   832 ?        Ss   10:09   0:00 dhclient
pcp      71277  0.0  0.1 127060  8384 ?        S    Oct09   0:06 pmlogger
""".strip()

PS_AUXCWW_NG = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0  19356  1544 ?        Ss   May31   0:01 init
root      1821  0.0  0.0      0     0 ?        S    May31   0:29 kondemand/0
root     20357  0.0  0.0   9120   832 ?        Ss   10:09   0:00 dhclient
""".strip()

LIST_UNIT_FILES = """
UNIT FILE                                   STATE
pmlogger.service                            enabled
pmlogger_check.service                      disabled
pmlogger_daily-poll.service                 static
pmlogger_daily.service                      static
pmproxy.service                             enabled

5 unit files listed.
""".strip()

LIST_UNIT_FILES_no_pmproxy = """
UNIT FILE                                   STATE
pmlogger.service                            enabled
pmlogger_check.service                      disabled
pmlogger_daily-poll.service                 static
pmlogger_daily.service                      static

5 unit files listed.
""".strip()

ROS_CONFIG = """
log mandatory on default {
    mem.util.used
    kernel.all.cpu.user
    disk.all.total
    mem.util.free
}
[access]
disallow .* : all;
disallow :* : all;
allow local:* : enquire;
""".strip()

ROS_CONFIG_NG = """
log mandatory off {
    mem.util.used
    kernel.all.cpu.user
    disk.all.total
    mem.util.free
}
[access]
disallow .* : all;
disallow :* : all;
allow local:* : enquire;
"""


def test_pcp_enabled():
    unitfiles = UnitFiles(context_wrap(LIST_UNIT_FILES))
    services = Services(None, unitfiles)
    broker = dr.Broker()
    broker[Services] = services

    result = pcp_enabled(broker)
    assert result is True

    unitfiles = UnitFiles(context_wrap(LIST_UNIT_FILES_no_pmproxy))
    services = Services(None, unitfiles)
    broker = dr.Broker()
    broker[Services] = services

    with pytest.raises(SkipComponent):
        pcp_enabled(broker)


@patch("insights.specs.datasources.pcp.os.path.exists", return_value=True)
@patch("insights.specs.datasources.pcp.os.path.isfile", return_value=True)
def test_pmlog_summary_args(isfile, exists):
    # Case 1: OK
    ros = RosConfig(context_wrap(ROS_CONFIG))
    ps_auxcww = PsAuxcww(context_wrap(PS_AUXCWW))
    ps = Ps(None, None, None, None, ps_auxcww, None, None)

    broker = dr.Broker()
    broker[Ps] = ps
    broker[RosConfig] = ros

    pcp_log_date = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")
    mock_file = "/var/log/pcp/pmlogger/ros/%s.index" % (pcp_log_date)

    result = pmlog_summary_args(broker)

    metrics = ' '.join(sorted([i.strip() for i in ROS_CONFIG.split('\n')[1:5]]))
    expected = '{0} {1}'.format(mock_file, metrics)
    assert result == expected

    # Case 2 NG metrics
    ros = RosConfig(context_wrap(ROS_CONFIG_NG))
    broker = dr.Broker()
    broker[Ps] = ps
    broker[RosConfig] = ros

    with pytest.raises(SkipComponent):
        pmlog_summary_args(broker)

    # Case 3 No pmloger proc in ps
    ros = RosConfig(context_wrap(ROS_CONFIG))
    ps_auxcww = PsAuxcww(context_wrap(PS_AUXCWW_NG))
    ps = Ps(None, None, None, None, ps_auxcww, None, None)
    broker = dr.Broker()
    broker[Ps] = ps
    broker[RosConfig] = ros

    with pytest.raises(SkipComponent):
        pmlog_summary_args(broker)


@patch("insights.specs.datasources.pcp.os.path.exists", return_value=False)
def test_pmlog_summary_args_no_pmloger_file(isfile):
    ros = RosConfig(context_wrap(ROS_CONFIG))
    ps_auxcww = PsAuxcww(context_wrap(PS_AUXCWW))
    ps = Ps(None, None, None, None, ps_auxcww, None, None)

    broker = dr.Broker()
    broker[Ps] = ps
    broker[RosConfig] = ros

    with pytest.raises(SkipComponent):
        pmlog_summary_args(broker)
