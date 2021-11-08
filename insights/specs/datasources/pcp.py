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


@datasource(Ps, RosConfig, HostContext)
def pmlog_summary_args(broker):
    """
    Determines the pmlogger file and the metrics to collect via `pmlog_summary`

    Returns:
        str: Full arguments string that pass to the `pmlog_summary`

    Raises:
        SkipComponent: Raises when meeting one of the following scenario:
                       - No pmlogger process is running
                       - No pmloger file
                       - No "mandatory on" metrics in `config.ros`
    """
    ps = broker[Ps]

    if ps.search(COMMAND_NAME__contains='pmlogger'):
        pcp_log_date = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")
        pm_file = "/var/log/pcp/pmlogger/ros/%s.index" % (pcp_log_date)
        try:
            if not (os.path.exists(pm_file) and os.path.isfile(pm_file)):
                raise SkipComponent("No such file: {0}".format(pm_file))
        except Exception as e:
            raise SkipComponent("Failed to check for pmlogger file existence: {0}".format(str(e)))

        metrics = set()
        ros = broker[RosConfig]
        for spec in ros.specs:
            if spec.get('state') == 'mandatory on':
                metrics.update(spec.get('metrics').keys())

        if not metrics:
            raise SkipComponent("No 'mandatory on' metrics in config.ros")

        return "{0} {1}".format(pm_file, ' '.join(sorted(metrics)))

    raise SkipComponent
