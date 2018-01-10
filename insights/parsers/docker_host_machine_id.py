"""
docker_host_machineid_parser - File ``/etc/redhat-access-insights/machine-id``
==============================================================================

This is a fairly simple function to read the Insights machine ID.

Because of the way this parser is used in the docker rules, this returns a
one-element dictionary with the machine ID referred to by the key
``host_system_id``.

Examples:

    >>> docker_info = {}
    >>> if docker_host_machineid_parser in shared:
    ...     docker_info.extend(shared[docker_host_machineid_parser])
    >>> docker_info
    { 'host_system_id': '123456789' }

"""

from .. import parser
from insights.specs import Specs


@parser(Specs.docker_host_machine_id)
def docker_host_machineid_parser(context):
    """
    Returns:
        (dict): Return the Insights machine ID in a dict with the key
        'host_system_id'.
    """
    content = list(context.content)[0]
    return {"host_system_id": content}
