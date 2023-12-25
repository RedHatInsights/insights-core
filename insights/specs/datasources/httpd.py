"""
Custom datasources related to ``httpd``
"""
import glob
import json
import os

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


def _get_all_include_conf(root, glob_path):
    includes = glob_path
    # In case $ServerRoot in included in the 'glob_path'
    if not glob_path.startswith(root):
        includes = os.path.join(root, glob_path)
    _paths = set()
    try:
        for conf in glob.glob(includes):
            if os.path.isfile(conf):
                _paths.add(conf)
                with open(conf) as cfp:
                    _includes = None
                    for line in cfp.readlines():
                        if line.strip().startswith("Include"):
                            _includes = line.split()[-1].strip('"\'')
                            _paths.update(_get_all_include_conf(root, _includes))
            if os.path.isdir(conf):
                _includes = os.path.join(conf, "*")
                _paths.update(_get_all_include_conf(root, _includes))
        return _paths
    except Exception:
        pass
    return _paths


def get_httpd_configuration_files(httpd_root):
    main_httpd_conf = os.path.join(httpd_root, "conf/httpd.conf")
    all_paths = set()
    try:
        with open(main_httpd_conf) as cfp:
            server_root = httpd_root
            # Add it only when it exists
            all_paths.add(main_httpd_conf)
            for line in cfp.readlines():
                if line.strip().startswith("ServerRoot"):
                    server_root = line.strip().split()[-1].strip().strip('"\'')
                elif line.strip().startswith("Include"):
                    includes = line.strip().split()[-1].strip('"\'')
                    # For multiple "Include" directives, all of them will be included
                    all_paths.update(_get_all_include_conf(server_root, includes))
    except Exception:
        # Skip the datasource when no such "<root path>/httpd.conf" file
        raise SkipComponent
    return all_paths


@datasource(HostContext)
def httpd_configuration_files(broker):
    """
    This datasource returns the all of httpd configuration files' path.

    Returns:
        list: the file path of httpd configuration files

    Raises:
        SkipComponent: there is no httpd configuration file
    """
    httpd_root = '/etc/httpd'
    all_paths = get_httpd_configuration_files(httpd_root)
    if all_paths:
        return all_paths
    raise SkipComponent


@datasource(HostContext)
def httpd24_scl_configuration_files(broker):
    """
    This datasource returns the all of httpd24 slc configuration files' path.

    Returns:
        list: the file path of httpd24 slc configuration files

    Raises:
        SkipComponent: there is no httpd24 slc configuration file
    """
    httpd_root = '/opt/rh/httpd24/root/etc/httpd'
    all_paths = get_httpd_configuration_files(httpd_root)
    if all_paths:
        return all_paths
    raise SkipComponent


@datasource(HostContext)
def httpd24_scl_jbcs_configuration_files(broker):
    """
    This datasource returns the all of httpd24 slc jbcs configuration files' path.

    Returns:
        list: the file path of httpd24 slc jbcs configuration files

    Raises:
        SkipComponent: there is no httpd24 slc jbcs configuration file
    """
    httpd_root = '/opt/rh/jbcs-httpd24/root/etc/httpd'
    all_paths = get_httpd_configuration_files(httpd_root)
    if all_paths:
        return all_paths
    raise SkipComponent
