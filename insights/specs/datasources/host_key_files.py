"""
Custom datasources relate to `/etc/*host*_key`
"""

import os

from insights.specs import Specs
from insights.core.context import HostContext
from insights.core.filters import add_filter
from insights.core.plugins import datasource
from insights.core.exceptions import SkipComponent
from insights.core.spec_factory import DatasourceProvider

ERROR_MSG = "error: Could not load host key:"
add_filter(Specs.messages, ERROR_MSG)


@datasource(Specs.messages, HostContext)
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
    error_loadings = set()
    messages = broker[Specs.messages].content
    for line in messages:
        if ERROR_MSG in line:
            error_loadings.add(line.split(ERROR_MSG)[-1].strip())

    if not error_loadings:
        raise SkipComponent()

    data_list = []
    for key_file in [file for file in error_loadings if file.startswith('/etc/')]:
        count = 0
        if os.path.exists(key_file):
            count = 1
        data_list.append("{0}   {1}".format(key_file, count))

    return DatasourceProvider(
        content="\n".join(data_list),
        relative_path='insights_datasources/host_key_files',
    )
