"""
Custom datasources for ``ls`` commands
"""
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.filters import add_filter, get_filters
from insights.core.plugins import datasource
from insights.specs import Specs


def _list_items(spec, broker):
    """Return a string of directories according to the spec filters."""
    datasource_list = sorted(get_filters(spec))
    if datasource_list:
        filters = []
        for item in datasource_list:
            spec = getattr(Specs, item)
            filters.extend(broker[spec].content)
        return ' '.join(filters)
    raise SkipComponent


@datasource(HostContext)
def list_with_lad_specific_file(broker):
    add_filter(Specs.ls_lad_specific_file_dirs, 'fstab_mounted')
    return _list_items(Specs.ls_lad_specific_file_dirs, broker)
