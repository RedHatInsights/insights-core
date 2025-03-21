"""
Custom datasource to get the current kernel version.
"""

from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.filters import get_filters
from insights.core.plugins import datasource
from insights.parsers.lsmod import LsMod
from insights.parsers.uname import Uname
from insights.specs import Specs


@datasource(Uname, HostContext)
def current_version(broker):
    """
    This datasource provides the current booting kernel version.

    Sample data returned::

        '4.18.0-240.el8.x86_64'

    Returns:
        String: The current kernel version.

    Raises:
        UnameError: When there is a problem occurs with uname data.
    """

    return broker[Uname].kernel


@datasource(Specs.grubby_default_kernel, HostContext)
def default_version(broker):
    """
    This datasource provides the default kernel version.

    Sample data returned::

        '4.18.0-240.el8.x86_64'

    Returns:
        String: The default kernel version.

    Raises:
        SkipComponent: When output is empty or an error occurs
    """
    try:
        content = broker[Specs.grubby_default_kernel].content
        if len(content) == 1 and len(content[0].split()) == 1:
            default_kernel = content[0]
            return default_kernel.lstrip("/boot/vmlinuz-")
    except Exception as e:
        raise SkipComponent("Unexpected exception:{e}".format(e=str(e)))
    raise SkipComponent


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
            module_list = [module for module in broker[LsMod].data if item in module]
            if module_list:
                loaded_modules.extend(module_list)
        if loaded_modules:
            return str(' '.join(loaded_modules))
        raise SkipComponent
    raise SkipComponent
