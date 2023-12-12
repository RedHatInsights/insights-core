"""
Custom datasource to get all updated/created eap reports in last 24 hours
"""

import os

from insights.core.context import HostContext
from insights.core.plugins import datasource
from insights.core.exceptions import SkipComponent
from insights.specs.datasources import get_recent_files


@datasource(HostContext)
def eap_report_files(broker):
    """
    Get all updated/created eap reports in last 24 hours.

    Returns:
        function: return the list of EAP reports file in last 24 hours.
    """
    ctx = broker[HostContext]
    root = ctx.root
    EAP_REPORTS_JSON_PATH = os.path.join(root, "var/tmp/insights-runtimes/uploads/")
    final_files = get_recent_files(EAP_REPORTS_JSON_PATH, 24)
    if final_files:
        return [f[len(root):] for f in final_files]
    raise SkipComponent
