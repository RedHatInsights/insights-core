"""
Custom datasources to get a list of directories to check disk size.
"""

from insights.core.context import HostContext
from insights.core.plugins import datasource
from insights.core.filters import get_filters
from insights.specs import Specs


@datasource(HostContext)
def du_dirs_list(broker):
    """ Return a list of directories from the spec filter """
    filters = get_filters(Specs.du_dirs)
    return list(filters)
