"""
Custom datasource related PCP (Performance Co-Pilot)
"""
import logging
import datetime
import os

from insights.core.dr import SkipComponent
from insights.core.context import HostContext
from insights.core.plugins import datasource
from insights.parsers.ros_config import RosConfig
from insights.combiners.ps import Ps
from insights.combiners.services import Services

logger = logging.getLogger(__name__)


@datasource(Services, HostContext)
def pcp_enabled(broker):
    """
    Returns:
        bool: True if pmproxy service is on in services

    Raises:
        SkipComponent: When pmproxy service is not enabled
    """
    if not broker[Services].is_on("pmproxy"):
        raise SkipComponent("pmproxy not enabled")
    return True


@datasource(Ps, HostContext)
def pmlog_summary_file(broker):
    """
    Determines the name for the pmlogger file and checks for its existence

    Returns the name of the latest pmlogger summary file if a running ``pmlogger``
    process is detected on the system.

    Returns:
        str: Full path to the latest pmlogger file

    Raises:
        SkipComponent: Raises this exception when the command is not present or
            the file is not present
    """
    ps = broker[Ps]
    if ps.search(COMMAND_NAME__contains='pmlogger'):
        pcp_log_date = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")
        file = "/var/log/pcp/pmlogger/ros/%s.index" % (pcp_log_date)
        try:
            if os.path.exists(file) and os.path.isfile(file):
                return file
        except Exception as e:
            SkipComponent("Failed to check for pmlogger file existence: {0}".format(str(e)))

    raise SkipComponent


@datasource(RosConfig, HostContext)
def pmlog_summary_metrics(broker):
    """
    Returns the metrics specified as "mandatory on" in the `config.ros` file
    for the pmlogger summary file.

    Returns:
        str: Full path to the latest pmlogger file

    Raises:
        SkipComponent: When no metrics get from the RosConfig
    """
    ros = broker[RosConfig]
    metrics = set()

    for spec in ros.specs:
        if spec.get('state') == 'mandatory on':
            metrics.update(spec.get('metrics').keys())

    if metrics:
        return ' '.join(sorted(metrics))

    raise SkipComponent
