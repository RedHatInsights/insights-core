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
        data: ``int`` if nova user exist otherwise ``None``.

    Raises:
        SkipException: If output is empty.
        ParseException: If nova user not found,
    '''
    def parse_content(self, content):
        self.data = None
        if not content:
            raise SkipException()
        if len(content) == 1:
            if "no such user" in content[0]:
                raise ParseException('No such user.')
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
        data: ``int`` if nova_migration user exist otherwise ``None``.

    Raises:
        SkipException: If output is empty.
        ParseException: If nova_migration user not found.

    '''
    pass
