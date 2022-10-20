"""
SELinux Policy Management tool
==============================

This module contains the following parsers:

LinuxUserCountMapSelinuxUser - datasource ``users_count_map_selinux_user``
--------------------------------------------------------------------------
"""

from insights.specs import Specs
from insights import JSONParser, parser


@parser(Specs.users_count_map_selinux_user)
class LinuxUserCountMapSelinuxUser(JSONParser):
    """
    Parse the output of the datasource ``users_count_map_selinux_user``.
    It returns a dict by transforming the json format.

    Sample Input::

        {
            "staff_u": 2,
            "guest_u": 4
        }

    Examples:
        >>> from insights.core.filters import add_filter
        >>> from insights.specs import Specs
        >>> add_filter(Specs.selinux_users, 'staff_u')
        >>> add_filter(Specs.selinux_users, 'guest_u')
        >>> type(users)
        <class 'insights.parsers.semanage.LinuxUserCountMapSelinuxUser'>
        >>> 'staff_u' in users
        True
        >>> users['staff_u']
        2
    """
    pass
