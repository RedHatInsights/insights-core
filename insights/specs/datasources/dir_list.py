"""
Custom datasources to get a list of directories to check disk size.
"""

from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.core.filters import get_filters, add_filter
from insights.specs import Specs

add_filter(Specs.du_dirs, ['/', '/opt', '/home/liuxc'])


@datasource(HostContext, timeout=2)
def du_dir_list(broker):
    """ Return a list of directories from the spec filter """
    print('run du_dir_list')
    import time
    time.sleet(5)
    filters = list(get_filters(Specs.du_dirs))
    if filters:
        return filters
    raise SkipComponent
