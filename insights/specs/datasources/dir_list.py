"""
Custom datasources to get a list of directories to check disk size.
"""
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.filters import get_filters
from insights.core.plugins import datasource
from insights.specs import Specs


@datasource(HostContext)
def du_dir_list(broker):
    """ Return a list of directories from the spec filter """
    filters = list(get_filters(Specs.du_dirs))
    if filters:
        return filters
    raise SkipComponent
