"""
Custom datasources related to ``httpd``
"""
import json

from insights.combiners.ps import Ps
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider
from insights.parsers.mount import ProcMounts
from insights.specs.datasources import get_running_commands


@datasource(Ps, HostContext)
def httpd_cmds(broker):
    """
    Function to search the output of ``ps auxcww`` to find all running Apache
    webserver processes and extract the binary path.

    Returns:
        list: List of the binary paths to each running process
    """
    cmds = get_running_commands(broker[Ps], broker[HostContext], ['httpd', ])
    if cmds:
        return cmds
    raise SkipComponent


@datasource(ProcMounts, HostContext)
def httpd_on_nfs(broker):
    """
    Function to get the count of httpd opened file on nfs v4

    Returns:
        str: JSON string with keys: "httpd_ids", "nfs_mounts", "open_nfs_files"
    """
    mnt = broker[ProcMounts]
    mps = mnt.search(mount_type='nfs4')
    # get nfs 4.0 mount points
    nfs_mounts = [m.mount_point for m in mps if 'vers' in m.mount_options and m.mount_options.vers.startswith("4")]
    if nfs_mounts:
        # get all httpd ps
        httpd_pids = broker[HostContext].shell_out("pgrep httpd")
        if httpd_pids:
            open_nfs_files = 0
            lsof_cmds = ["lsof -p {0}".format(pid) for pid in httpd_pids if pid]
            # maybe there are thousands open files
            for cmd in lsof_cmds:
                for line in broker[HostContext].shell_out(cmd):
                    items = line.split()
                    if len(items) > 8 and items[8].startswith(tuple(nfs_mounts)):
                        open_nfs_files += 1
            result_dict = {"http_ids": httpd_pids, "nfs_mounts": nfs_mounts, "open_nfs_files": open_nfs_files}
            relative_path = 'insights_commands/httpd_open_nfsV4_files'
            return DatasourceProvider(content=json.dumps(result_dict), relative_path=relative_path)
    raise SkipComponent
