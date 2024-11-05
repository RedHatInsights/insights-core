"""
Custom datasources for ``ls`` commands
"""
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.specs import Specs
from insights.parsers.fstab import FSTab
from insights.core.filters import get_filters
from insights.core.filters import add_filter


def _list_items(spec, broker):
    """Return a tuple of directories according to the spec filters."""
    datasource_list = sorted(get_filters(spec))
    if datasource_list:
        filters = []
        for item in datasource_list:
            spec = getattr(Specs, item)
            filters.extend(broker[spec].content)
        return ' '.join(filters)
    raise SkipComponent


@datasource(FSTab, HostContext)
def fstab_mounted(broker):
    """
    This datasource provides a list of the /etc/fstab mount points.

    Sample data returned::

        '/ /boot'

    Returns:
        list: List of the /etc/fstab mount points.

    Raises:
        SkipComponent: When there is not any mount point.
    """
    content = broker[FSTab].data
    if content:
        fs_mount_point = []
        for item in content:
            fs_mount_point.append(item['fs_file'])
        return ' '.join(fs_mount_point)

    raise SkipComponent


@datasource(HostContext)
def list_with_lad_specific_file(broker):
    add_filter(Specs.ls_lad_specific_file_dirs, 'fstab_mounted')
    return _list_items(Specs.ls_lad_specific_file_dirs, broker)
