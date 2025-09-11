"""
Custom datasources for logrotate
"""

import os

from insights.core.context import HostContext
from insights.core.plugins import datasource


@datasource(HostContext)
def logrotate_conf_list(broker):
    """
    This datasource returns the list of logrotate configuration files.
    - "/etc/logrotate.conf" is the one must be collected.
    - Files without extension under "/etc/logrotate.d/" will be collected.
    - Files with extension, only the ".conf" files will be collected.

    Returns:
        list: The list of logrotate configuration files.
              ["/etc/logrotate.conf"] by default
    """
    conf_files = ["/etc/logrotate.conf"]
    root = "/etc/logrotate.d/"
    if os.path.isdir(root):
        for file_name in os.listdir(root):
            file_path = os.path.join(root, file_name)
            if ('.' not in file_name or file_name.endswith('.conf')) and os.path.isfile(file_path):
                conf_files.append(file_path)
    return conf_files
