"""
Custom datasource to get the linux users count who map to a selinux user.
"""
import json

from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.filters import get_filters
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider, simple_command
from insights.parsers import parse_fixed_table
from insights.specs import Specs


class LocalSpecs(Specs):
    """ Local specs used only by users_count_map_selinux_user datasource """

    selinux_user_mapping = simple_command("/sbin/semanage login -l")


@datasource(LocalSpecs.selinux_user_mapping, HostContext)
def users_count_map_selinux_user(broker):
    """
    Get linux users count who map to the selinux user. It returns a dict with
    the selinux user type as the key, and the linux users count as the value.

    Raises:
        SkipComponent: Raised when there are no users map the filtered selinux user.
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
    filters = sorted((get_filters(Specs.selinux_users)))
    users_info = {}
    for filter in filters:
        users_info[filter] = len([obj for obj in data if obj['selinux_user'] == filter])
    if users_info:
        return DatasourceProvider(json.dumps(users_info), relative_path='insights_commands/linux_users_count_map_selinux_user')
    raise SkipComponent
