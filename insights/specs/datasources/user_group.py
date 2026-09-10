"""
Custom datasources for user and group related specs

.. note::
    It should be noted that the specs in this module might contains sensitive
    information, please avoid collecting any of them.
"""

import pwd

from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.filters import get_filters
from insights.core.plugins import datasource
from insights.specs import Specs


@datasource(HostContext)
def all_users(broker):
    """
    Return the full passwd database (``pwd.getpwall()``) as a list of
    ``pwd.struct_passwd`` entries.

    ``pwd.getpwall()`` can be expensive on hosts with many users (for example
    LDAP-backed systems), so this datasource centralises the lookup: other
    datasources depend on it instead of calling ``pwd.getpwall()`` themselves,
    and the broker caches the result so the lookup runs only once per
    collection.

    This is an internal helper datasource. It is not registered as a spec and
    returns a plain list rather than a
    :class:`insights.core.spec_factory.DatasourceProvider`, so its output is
    never written to the archive.

    Raises:
        SkipComponent: When no users are found.
    """
    users = pwd.getpwall()
    if not users:
        raise SkipComponent("No users found")
    return users


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
