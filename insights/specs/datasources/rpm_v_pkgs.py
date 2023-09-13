"""
Custom datasources for ``/bin/rpm -V <package>`` commands
"""
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.filters import get_filters
from insights.core.plugins import datasource
from insights.specs import Specs


def _list_items(spec):
    """Return a tuple of directories according to the spec filters."""
    filters = sorted(get_filters(spec))
    if filters:
        return filters
    raise SkipComponent


@datasource(HostContext)
def list_with_pkgs(broker):
    return _list_items(Specs.rpm_V_package_list)
