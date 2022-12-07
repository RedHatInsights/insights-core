"""
Custom datasource to get the current kernel version.
"""

from insights.core.context import HostContext
from insights.core.plugins import datasource
from insights.parsers.uname import Uname


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
