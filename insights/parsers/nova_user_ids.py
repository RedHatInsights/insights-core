"""
Get ``uid`` of user ``nova`` and ``nova_migration``
===================================================

The parser class in this module uses base parser class
``CommandParser`` to get uids of the user ``nova`` and
``nova_migration``.

Parsers included in this module are:

NovaUID - command ``id -u nova``
--------------------------------

NovaMigrationUID - command ``id -u nova_migration``
---------------------------------------------------
"""
from insights import CommandParser, parser
from insights.parsers import ParseException, SkipException
from insights.specs import Specs


@parser(Specs.nova_uid)
class NovaUID(CommandParser):
    '''Parse output of ``id -u nova`` and get the ``uid`` (int).

    Typical output of the ``id -u nova`` command is::

        162

    However the id number may vary.

    Examples:

        >>> nova_uid.data
        162

    Attributes:
        data: ``int`` if 'nova' user exist.

    Raises:
        SkipException: If 'nova' user not found or output is empty.
        ParseException: For any other output which is not a number or multi-line.
            Outputs of such kind are not yet expected from the command `id`.
    '''
    def parse_content(self, content):
        if not content:
            raise SkipException("Empty output.")
        if "no such user" in content[0].lower():
            raise SkipException("No such user.")
        if len(content) > 1 or not content[0].isdigit():
            raise ParseException("Unable to parse user ID: {0}".format(content))
        self.data = int(content[0])


@parser(Specs.nova_migration_uid)
class NovaMigrationUID(NovaUID):
    '''Parse output of ``id -u nova_migration`` and get the ``uid`` (int).

    Typical output of the ``id -u nova_migration`` command is::

        153

    However the id number may vary.

    Examples:

        >>> nova_migration_uid.data
        153

    Attributes:
        data: ``int`` if 'nova_migration' user exist.

    Raises:
        SkipException: If 'nova_migration' user not found or output is empty.
        ParseException: For any other output which is not a number or multi-line.
            Output of such kind are not yet expected from the command `id`.
    '''
    pass
