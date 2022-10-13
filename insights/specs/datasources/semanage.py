"""
Custom datasources to get the linux users count which map to a staff_u selinux user.
"""

from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider, simple_command
from insights.specs import Specs
from insights.parsers import parse_fixed_table


class LocalSpecs(Specs):
    """ Local specs used only by users_count_map_staff_u_selinux_user datasource """

    selinux_user_mapping = simple_command("/sbin/semanage login -l")


@datasource(LocalSpecs.selinux_user_mapping, HostContext)
def users_count_map_staff_u_selinux_user(broker):
    """
    Get linux users count who map to the staff_u selinux user.

    Returns:
        str: The users count who map to the staff_u selinux user.

    Raises:
        SkipComponent: Raised when there is no users map to staff_u selinux user.
    """
    user_mapping_lines = broker[LocalSpecs.selinux_user_mapping].content
    data = parse_fixed_table(
        user_mapping_lines,
        heading_ignore=['Login Name'],
        header_substitute=[
            ('Login Name', 'login_name'),
            ('SELinux User', 'selinux_user'),
            ('MLS/MCS Range', 'mls_mcs_range'),
            ('Service', 'service'),
        ]
    )
    staff_u_users = [obj for obj in data if obj['selinux_user'] == 'staff_u']
    if staff_u_users:
        return DatasourceProvider(str(len(staff_u_users)), relative_path='insights_commands/linux_users_count_map_staff_u_selinux_user')
    raise SkipComponent
