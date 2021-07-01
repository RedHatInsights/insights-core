"""
Custom datasources to get the semid of all the inter-processes.
"""

from insights.core.context import HostContext
from insights.core.spec_factory import simple_command
from insights.core.plugins import datasource
from insights.specs import Specs
from insights.core.dr import SkipComponent


class LocalSpecs(Specs):
    """ Local specs used only by semid datasources """

    ipcs_s_cmd = simple_command("/usr/bin/ipcs -s")


@datasource(LocalSpecs.ipcs_s_cmd, HostContext)
def semid(broker):
    """
    This datasource provides a list of the semid of all the inter-processes.

    Note:
        This datasource may be executed using the following command:

        ``insights cat --no-header ipcs_s_i``

    Sample output::

        [
            '65570', '98353', '98354'
        ]

    Returns:
        list: A list of the semid of all the inter-processes.
    """
    content = broker[LocalSpecs.ipcs_s_cmd].content
    results = set()
    for s in content:
        s_splits = s.split()
        # key        semid      owner      perms      nsems
        # 0x00000000 65536      apache     600        1
        if len(s_splits) == 5 and s_splits[1].isdigit():
            results.add(s_splits[1])
    if results:
        return list(results)
    raise SkipComponent
