"""
Custom datasources to get a list of modules to check the detailed module info.
"""

from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.core.filters import get_filters
from insights.specs import Specs


@datasource(HostContext)
def kernel_module_filters(broker):
    """
    Return a string of a list of modules from the spec filter,
    separated with space.
    """
    filters = sorted((get_filters(Specs.modinfo_modules)))
    if filters:
        return ' '.join(filters)
    raise SkipComponent
