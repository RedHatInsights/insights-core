"""
Custom datasource related PCP (Performance Co-Pilot)
"""
import datetime
import glob
import logging
import os

from insights.combiners.ps import Ps
from insights.combiners.services import Services
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent, ContentException
from insights.core.plugins import datasource
from insights.parsers.hostname import Hostname, HostnameDefault
from insights.parsers.ros_config import RosConfig

logger = logging.getLogger(__name__)

pcp_metrics = [
        'disk.dev.total',
        'hinv.ncpu',
        'kernel.all.cpu.idle',
        'kernel.all.pressure.cpu.some.avg',
        'kernel.all.pressure.io.full.avg',
        'kernel.all.pressure.io.some.avg',
        'kernel.all.pressure.memory.full.avg',
        'kernel.all.pressure.memory.some.avg',
        'mem.physmem',
        'mem.util.available',
]


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


@datasource(HostContext)
def ros_collect(broker):
    """
    Returns:
        bool: True if "ros_collect=True" is set in "insights-client.conf"

    Raises:
        SkipComponent: When "ros_collect=True" is not set
    """
    insights_config = broker.get('client_config')
    if insights_config and insights_config.ros_collect is True:
        return True
    raise SkipComponent


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


@datasource(ros_collect, [Hostname, HostnameDefault], HostContext)
def pcp_raw_files(broker):
    """
    Return all existing paths of PCP RAW data files of yesterday.

    .. note::
        The "hostname" in the file paths will be removed by the "save_as"
        in the `pcp_raw_data` spec.  All the collected PCP RAW data files
        will be stored in "var/log/pcp/pmlogger" directory in the archive.

    Returns:
        list(str): list of file path

    Raises:
        ContentException: Raises when no such directory or number of PCP RAW
                          files less than 3.
    """
    hostnames = set()
    hnd = broker.get(HostnameDefault)
    hostnames.add(hnd.raw) if hnd else None
    hn = broker.get(Hostname)
    hostnames.update([hn.hostname, hn.fqdn]) if hn else None

    pm_cand = []
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")
    for hostname in sorted(hostnames):
        pm_root = os.path.join("/var/log/pcp/pmlogger/", hostname)
        if os.path.exists(pm_root):
            pm_files = glob.glob(os.path.join(pm_root, "{0}.*.xz".format(yesterday)))
            pm_files.append(os.path.join(pm_root, "{0}.index".format(yesterday)))
            pm_files = sorted(set(filter(lambda x: os.path.isfile(x), pm_files)))
            if len([pf for pf in pm_files if pf.endswith(('.index', '.meta.xz', '.0.xz'))]) >= 3:
                pm_cand.append((pm_files, os.path.getmtime(pm_files[-2])))  # timestamp of '.index'

    if not pm_cand:
        raise ContentException("No PCP data directory OR incomplete PCP RAW data")

    # return the "pm_files" which:
    # 1. has latest yesterday ".index"
    # 2. has complete data (>=3)
    # 3. has much more data than others
    #    - a rare case: when multiple pm_files satisfy with both 1 and 2
    return sorted(pm_cand, key=lambda x: (x[1], len(x[0])))[-1][0]


@datasource(pcp_raw_files, HostContext)
def pmlog_summary_args_pcp_zeroconf(broker):
    """
    Return the 'index' of the PCP Raw data files and the required metrics.

    Returns:
        str: Full arguments string that will be passed to the `pmlogsummary`,
             which contains the `pmlogger` index file and the required `metrics`.
    """
    pm_files = broker.get(pcp_raw_files)
    pm_index = [fil for fil in pm_files if fil.endswith('.index')][0]
    return "{0} {1}".format(pm_index, ' '.join(pcp_metrics))
