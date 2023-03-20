"""
Custom datasources to get a list of modules to check the detailed module info.
"""
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.filters import get_filters
from insights.core.plugins import datasource
from insights.parsers.lsmod import LsMod
from insights.specs import Specs


@datasource(LsMod, HostContext)
def kernel_module_filters(broker):
    """
    Return a string of a list of modules from the spec filter,
    separated with space.
    """
    filters = sorted((get_filters(Specs.modinfo_modules)))
    if filters:
        loaded_modules = []
        for item in filters:
            if item in broker[LsMod]:
                loaded_modules.append(item)
        if loaded_modules:
            return ' '.join(loaded_modules)
        raise SkipComponent
    raise SkipComponent
