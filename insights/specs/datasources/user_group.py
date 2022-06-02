"""
Custom datasources for user and group related specs

.. note::
    It should be noted that the specs in this module might contains sensitive
    information, please avoid collecting any of them.
"""
from insights.specs import Specs
from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.core.filters import get_filters


@datasource(HostContext)
def group_filters(broker):
    """
    Return a string contains the list of groups getting from the spec filter,
    separated with space.
    """
    grp_list = sorted(get_filters(Specs.group_info))
    if grp_list:
        return ' '.join(grp_list)
    raise SkipComponent
