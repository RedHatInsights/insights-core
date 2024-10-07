"""
Custom datasources for environments.
"""
import re
import os

from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider


@datasource(HostContext)
def ld_library_path_of_global(broker):
    """
    This datasource gets the LD_LIBRARY_PATH enviorment setting for root user,
    if it's set, then reads the following config files:
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
    returns the config files that include the config.

    The output of this datasource looks like:
        /etc/environment
        /root/.profile
    Returns:
        str: Returns a multiline string, each line represent a config file. Not return
             the value of enviorment, because it might include sensitive information.
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
        "/root/.tcshrc"
    ]
    data = []

    for item in config_files:
        if (os.path.exists(item) and
                os.path.isfile(item) and
                _is_env_exported(item, env_name)):
            data.append(item)
        elif os.path.exists(item) and os.path.isdir(item):
            for file_name in os.listdir(item):
                file_path = os.path.join(item, file_name)
                if (os.path.isfile(file_path) and
                        _is_env_exported(file_path, env_name)):
                    data.append(file_path)

    if not data:
        raise SkipComponent()

    return DatasourceProvider(content="\n".join(data), relative_path='insights_commands/ld_library_path_of_global')


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
        for line in file.readlines():
            line = line.strip()
            if not line or line.startswith("#") or line.split()[0] != "export":
                continue
            if re.search(pattern, line):
                return True
    return False
