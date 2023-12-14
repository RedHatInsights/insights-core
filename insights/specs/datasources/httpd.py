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


@datasource(HostContext)
def httpd_configuration_files(broker):
    """
    This datasource returns the all of httpd configuration files' path.

    Returns:
        list: the file path of httpd configuration files

    Raises:
        SkipComponent: there is no httpd configuration file
    """

    all_paths = []
    default_paths = []
    main_httpd_conf = "/etc/httpd/conf/httpd.conf"
    if not os.path.isfile(main_httpd_conf):
        raise SkipComponent("/etc/httpd/conf/httpd.conf is not existing")
    all_paths.append(main_httpd_conf)
    default_paths.append(main_httpd_conf)

    server_root = "/etc/httpd"
    with open(main_httpd_conf) as main_conf_file:
        for line in main_conf_file.readlines():
            if line.strip().startswith("ServerRoot"):
                server_root = line.strip().split()[-1].strip().replace("'", "").replace('"', '')

    genernation_dict = {1: default_paths}
    genernation = 1

    while genernation:
        new_include = False
        for item in genernation_dict[genernation]:
            with open(item) as conf_file:
                read_content = conf_file.read()
                conf_file.seek(0)
                readlines_content = conf_file.readlines()
                if "Include" in read_content or "IncludeOptional" in read_content:
                    for line in readlines_content:
                        if line.strip().startswith("Include") or line.strip().startswith("IncludeOptional"):
                            include_file_path = line.strip().split()[-1].strip()
                            if not include_file_path.startswith("/"):
                                include_file_path = os.path.join(server_root, include_file_path)
                            all_include_files = glob.glob(include_file_path)
                            for file in all_include_files:
                                if os.path.isfile(file):
                                    all_paths.append(file)
                                    with open(file) as include_conf_file:
                                        include_read_content = include_conf_file.read()
                                        if "Include" in include_read_content or "IncludeOptional" in include_read_content:
                                            if not new_include:
                                                genernation = genernation + 1
                                            new_include = True
                                            if genernation in genernation_dict:
                                                genernation_dict[genernation].append(file)
                                            else:
                                                genernation_dict[genernation] = [file]
        if not new_include:
            genernation = 0

    if all_paths:
        return all_paths
    raise SkipComponent
