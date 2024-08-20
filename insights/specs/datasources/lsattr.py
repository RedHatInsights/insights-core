"""
Custom datasources for ``lsattr`` command
"""
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.filters import get_filters
from insights.core.plugins import datasource
from insights.specs import Specs


@datasource(HostContext)
def paths_to_lsattr(broker):
    """
    Get the files or directories by the filters from Specs.lsattr_files_or_dirs

    Returns:
        str: A string by joining all the paths by whitespace

    Raises:
        SkipComponent: when there is not any filter
    """
    filters = sorted(get_filters(Specs.lsattr_files_or_dirs))
    if filters:
        return ' '.join(filters)
    raise SkipComponent
