"""
BadOwnershipOfVarOptMSSql - datasource ``ownership_of_var_opt_mssql``
=====================================================================
"""
import json
from insights.specs import Specs
from insights.parsers import SkipException
from .. import CommandParser, parser


@parser(Specs.ownership_of_var_opt_mssql)
class BadOwnershipOfVarOptMSSql(CommandParser):
    """Return the ownership of /var/opt/mssql if it is not ``mssql:mssql``

    Attributes:
        (dict): Ex: {"owner": "foo", "group": "bar"}

    Raises:
        SkipException: If Correct ownership of /var/opt/mssql.

    The following are available in ``data``:

        * ``owner`` - dir owner
        * ``group`` - dir group
    """
    def parse_content(self, content):
        if not content:
            raise SkipException('Correct ownership of /var/opt/mssql.')
        self.data = json.loads(''.join(content))
