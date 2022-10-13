"""
SELinux Policy Management tool
==============================

This module contains the following parsers:

UsersCountMapStaffuSelinuxUser - datasource ``users_count_map_staff_u_selinux_user``
------------------------------------------------------------------------------------
"""

from insights.core.dr import SkipComponent
from insights.specs import Specs
from insights import Parser, parser


@parser(Specs.users_count_map_staff_u_selinux_user)
class UsersCountMapStaffuSelinuxUser(Parser):
    """
    Parse the output of the datasource ``users_count_map_staff_u_selinux_user``.
    It returns the linux user count who map to a staff_u selinux user.

    Attributes:
        count (int): the linux user count who map to a staff_u selinux user

    Raises:
        SkipComponent: The content is emtpy, has many lines or the content is not in int format.

    Examples:
        >>> users.count
        2
    """
    def parse_content(self, content):
        if len(content) != 1 or not (content[0].isdigit()):
            raise SkipComponent
        self.count = int(content[0])
