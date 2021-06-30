from insights.core.context import HostContext
from insights.core.plugins import datasource
from insights.parsers.ipcs import IpcsS


@datasource(HostContext, IpcsS)
def get_semid(broker):
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
    ipcs_obj = broker[IpcsS]
    return list(ipcs_obj.data.keys())
