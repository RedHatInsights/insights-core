"""
Custom datasource to get the current kernel version.
"""

from insights.core.context import HostContext
from insights.core.plugins import datasource
from insights.core.exceptions import SkipComponent
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
