"""
Custom datasource to get all updated/created eap reports in last 24 hours
"""
import os
import time
import logging

from insights.core.context import HostContext
from insights.core.plugins import datasource
from insights.core.exceptions import SkipComponent
from insights.core.spec_factory import TextFileProvider

log = logging.getLogger(__name__)


def get_recent_files(target_path, last_modify_hours):
    result_files = []
    if os.path.exists(target_path):
        current_time = time.time()
        for one_file in os.listdir(target_path):
            t_full_file = os.path.join(target_path, one_file)
            if os.path.isfile(t_full_file):
                file_time = os.path.getmtime(t_full_file)
                if (current_time - file_time) // 3600 < last_modify_hours:
                    result_files.append(t_full_file)
    return result_files


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
    results = []
    for full_path_file in final_files:
        results.append(TextFileProvider(full_path_file[len(root):], root=root, ds=eap_report_files, ctx=ctx))
    if results:
        return results
    raise SkipComponent
