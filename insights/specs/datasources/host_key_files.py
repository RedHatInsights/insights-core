"""
Custom datasources relate to `/etc/*dsa*_key`
"""

import os

from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider 

ERROR_KEY = "error: Could not load host key:"
VAR_LOG_MSG = '/var/log/messages'

@datasource(HostContext)
def host_key_files(broker):
    """
    This datasource reads '/var/log/messages' to check the host key path, and check
    whether the corresponding file exists.

    The output of this datasource looks like:
        /etc/ssh/ssh_host_dsa_key   1
        /etc/ssh_host_dsa_key   0

    Returns:
        str: Returns a multiline string in the format as ``file_path count``.

    Raises:
        SkipComponent: When any exception occurs.
    """
    error_loadings = []
    with open(VAR_LOG_MSG, 'r', encoding='utf-8') as file:
        for line in file:
            if ERROR_KEY in line:
                error_loadings.append(line.split(ERROR_KEY)[-1])

    if not error_loadings:
        raise SkipComponent()

    data_list = []
    for key_file in error_loadings:
        count = 0
        if os.path.exists(key_file):
            count = 1
        data_list.append("{0}   {1}".format(key_file, count))

    return DatasourceProvider(
        content="\n".join(data_list),
        relative_path='insights_datasources/host_key_files',
    )
