"""
Custom datasources for user and group related specs
"""
from insights.specs import Specs
from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.core.filters import get_filters


@datasource(HostContext)
def groups(broker):
    """
    Return a string contains the list of groups getting from the spec filter,
    separated with space.
    """
    groups = list(get_filters(Specs.group_info))
    if groups:
        return ' '.join(groups)
    raise SkipComponent
