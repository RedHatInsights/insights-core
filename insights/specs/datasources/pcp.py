"""
Custom datasources for performance co-pilot information
"""
import datetime
import os

from insights.combiners.ps import Ps
from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource


@datasource(Ps, HostContext)
def pmlog_summary_file(broker):
    """
    Determines the name for the pmlogger file and checks for its existance

    Returns the name of the latest pmlogger summary file if a running ``pmlogger``
    process is detected on the system.

    Returns:
        str: Full path to the latest pmlogger file

    Raises:
        SkipComponent: raises this exception when the command is not present or
            the file is not present
    """
    if broker[Ps].search(COMMAND__contains='pmlogger'):
        pcp_log_date = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")
        file = "/var/log/pcp/pmlogger/ros/%s.index" % (pcp_log_date)
        try:
            if os.path.exists(file) and os.path.isfile(file):
                return file
        except Exception as e:
            SkipComponent("Failed to check for pmlogger file existance: {0}".format(str(e)))

    raise SkipComponent()
