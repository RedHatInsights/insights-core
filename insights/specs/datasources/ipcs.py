"""
Custom datasources to get the semid of all the inter-processes.
"""
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.specs import Specs


@datasource(Specs.ipcs_s, HostContext)
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
    allowed_owners = ['root', 'apache', 'oracle']
    content = broker[Specs.ipcs_s].content
    results = set()
    for s in content:
        s_splits = s.split()
        # key        semid      owner      perms      nsems
        # 0x00000000 65536      apache     600        1
        if len(s_splits) == 5 and s_splits[1].isdigit() and s_splits[2] in allowed_owners:
            results.add(s_splits[1])
    if results:
        return list(results)
    raise SkipComponent
