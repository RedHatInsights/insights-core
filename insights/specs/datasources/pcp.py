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
    spec.

    Returns:
        str: Full arguments string that will be passed to the `pmlogsummary`,
             which contains the `pmlogger` archive file and the required `metrics`.

    Raises:
        SkipComponent: Raises when meeting one of the following scenario:
                       - No pmlogger process is running
                       - No pmlogger file
                       - No "mandatory on" metrics in `config.ros`
    """
    pm_file = None
    try:
        ps = broker[Ps]
        if not ps.search(COMMAND_NAME__contains='pmlogger'):
            raise SkipComponent("No 'pmlogger' is running")

        pcp_log_date = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")
        pm_file = "/var/log/pcp/pmlogger/ros/{0}.index".format(pcp_log_date)

        if not (os.path.exists(pm_file) and os.path.isfile(pm_file)):
            raise SkipComponent("No pmlogger archive file: {0}".format(pm_file))

    except Exception as e:
        raise SkipComponent("Failed to check pmlogger file existence: {0}".format(str(e)))

    metrics = set()
    try:
        ros = broker[RosConfig]
        for spec in ros.specs:
            if spec.get('state') == 'mandatory on':
                metrics.update(spec.get('metrics').keys())

        if not metrics:
            raise SkipComponent("No 'mandatory on' metrics in config.ros")

    except Exception as e:
        raise SkipComponent("Failed to get pmlogger metrics: {0}".format(str(e)))

    return "{0} {1}".format(pm_file, ' '.join(sorted(metrics)))
