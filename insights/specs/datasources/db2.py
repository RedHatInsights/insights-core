"""
Custom datasources to get the db2 users and database names.
"""

from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.combiners.ps import Ps
from insights.core.spec_factory import foreach_execute
from insights.specs import Specs


@datasource(Ps, HostContext)
def db2_users(broker):
    """
    This datasource get the name of the users running db2 databases

    Returns:
        list: the names of the users running db2 databases

    Raises:
        SkipComponent: there is no db2 users running db2 databases
    """
    ps = broker[Ps]
    ps_list = ps.search(COMMAND_NAME__contains="db2sysc")
    if ps_list:
        users_result = set(filter(None, [item.get("USER") for item in ps_list]))
        users_result.discard('root')
        if users_result:
            return sorted(users_result)
        raise SkipComponent("No db2 user is available")
    raise SkipComponent("No db2 database is running")


class LocalSpecs(Specs):
    db2_databases = foreach_execute(db2_users, "/usr/sbin/runuser -l  %s  -c 'db2 list database directory'")


@datasource(LocalSpecs.db2_databases, HostContext)
def db2_databases_info(broker):
    """
    This datasource get the name of the users running db2 databases and the database names

    Returns:
        list: the set of user names and database names

    Raises:
        SkipComponent: there is no db2 databases
    """
    result = set()
    for item in broker[LocalSpecs.db2_databases]:
        user = item.cmd.split()[2].strip()
        for line in item.content:
            if "Database name" in line:
                name = line.split("=")[-1].strip()
                result.add((user, name))
    if result:
        return sorted(result)
    raise SkipComponent("No db2 database is available")
