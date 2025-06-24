"""
Custom datasources for environments.
"""

import re
import os
import json

from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider


@datasource(HostContext)
def ld_library_path_global_conf(broker):
    """
    This datasource gets the global LD_LIBRARY_PATH enviorment setting.

    Reads the following config files:
      * /etc/environment
      * /etc/env.d/*
      * /etc/profile
      * /etc/profile.d/*
      * /etc/bashrc
      * /etc/bash.bashrc
      * /root/.bash_profile
      * /root/.bashrc
      * /root/.profile
      * /root/.cshrc
      * /root/.zshrc
      * /root/.tcshrc

    When a line likes `export LD_LIBRARY_PATH=$LD_LIBRARY_PATH` exists, the datasource
    records the config file as an export file. When a line likes `unset LD_LIBRARY_PATH`
    exists, the datasource records the config file as an unset file

    The output of this datasource looks like:
        {"export_files": ["/etc/environment", "/etc/env.d/test.conf", "/root/.bash_profile"], "unset_files": ["/etc/profile"]}

    Returns:
        str: Returns a JSON format string, `export_files` contains the config files that define the
             LD_LIBRARY_PATH, `unset_files` contains config files that unset the LD_LIBRARY_PATH.
             Not return the line, because it might include sensitive information.

    Raises:
        SkipComponent: When any exception occurs.
    """
    env_name = "LD_LIBRARY_PATH"
    config_files = [
        "/etc/environment",
        "/etc/env.d",
        "/etc/profile",
        "/etc/profile.d",
        "/etc/bashrc",
        "/etc/bash.bashrc",
        "/root/.bash_profile",
        "/root/.bashrc",
        "/root/.profile",
        "/root/.cshrc",
        "/root/.zshrc",
        "/root/.tcshrc",
    ]
    data = {}

    export_files = []
    unset_files = []

    for item in config_files:
        if os.path.exists(item) and os.path.isfile(item):
            if _is_env_exported(item, env_name):
                export_files.append(item)
            if _is_env_unset(item, env_name):
                unset_files.append(item)
        elif os.path.exists(item) and os.path.isdir(item):
            for file_name in os.listdir(item):
                # Only read the first level files here.
                # Per the test, only the first level files will be executed.
                file_path = os.path.join(item, file_name)
                if os.path.isfile(file_path) and _is_env_exported(file_path, env_name):
                    export_files.append(file_path)
                if os.path.isfile(file_path) and _is_env_unset(file_path, env_name):
                    unset_files.append(file_path)

    if export_files:
        data["export_files"] = export_files

    if unset_files:
        data["unset_files"] = unset_files

    if not data:
        raise SkipComponent()

    return DatasourceProvider(
        content=json.dumps(data), relative_path='insights_datasources/ld_library_path_global_conf'
    )


def _is_env_exported(file_path, env_name):
    # The logic here is:
    # cat <config_file>|grep -w LD_LIBRARY_PATH|grep -w export
    # To catch the following LD_LIBRARY_PATH env setting:
    # 1. export LD_LIBRARY_PATH=/test/path
    # 2. export     LD_LIBRARY_PATH
    # 3. export LD_LIBRARY_PATH=/test/path TEST=/path/to/test
    # There might be other syntaxs, they will not be collected.
    pattern = r"\b{0}\b".format(env_name)

    with open(file_path, 'r') as file:
        active_lines = list(
            filter(None, (line.split("#", 1)[0].strip() for line in file.readlines()))
        )
        for line in active_lines:
            if "export " in line and re.search(pattern, line):
                return True
    return False


def _is_env_unset(file_path, env_name):
    # if one line with "unset " + LD_LIBRARY_PATH
    # returns True
    pattern = r"\b{0}\b".format(env_name)

    with open(file_path, 'r') as file:
        active_lines = list(
            filter(None, (line.split("#", 1)[0].strip() for line in file.readlines()))
        )
        for line in active_lines:
            if "unset " in line and re.search(pattern, line):
                return True
    return False
