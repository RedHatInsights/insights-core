"""
Get ``uid`` of user ``nova`` and ``nova_migration``
=====================================================

The parser class in this module uses base parser class
``CommandParser`` to get uids of the user ``nova`` and
``nova_migration``.

Parsers included in this module are:

NovaUID - command ``id -u nova``
--------------------------------

NovaMigrationUID - command ``id -u nova_migration``
----------------------------------------------------
"""
from insights import CommandParser, parser
from insights.parsers import ParseException
from insights.specs import Specs


@parser(Specs.nova_uid)
class NovaUID(CommandParser):
    '''Parse output of ``id -u nova`` and get the ``uid`` (int).
    Return ``None`` if nova user not found.

    Typical output of the ``id -u nova`` command is::

        162

    However the id number may vary.

    Examples:

        >>> nova_uid.data
        162
        >>> nova_user_not_found.data is None
        True

    Attributes:
        data: ``int`` if nova user exist otherwise ``None``.

    '''
    def parse_content(self, content):
        self.data = None
        if not content:
            raise ParseException("Input content is empty.")
        if len(content) == 1 and "no such user" not in content[0]:
            self.data = int(content[0])


@parser(Specs.nova_migration_uid)
class NovaMigrationUID(CommandParser):
    '''Parse output of ``id -u nova_migration`` and get the ``uid`` (int).
    Return ``None`` if nova_migration user not found.

    Typical output of the ``id -u nova_migration`` command is::

        153

    However the id number may vary.

    Examples:

        >>> nova_migration_uid.data
        153
        >>> nova_migration_user_not_found.data is None
        True

    Attributes:
        data: ``int`` if nova_migration user exist otherwise ``None``.

    '''
    def parse_content(self, content):
        self.data = None
        if not content:
            raise ParseException("Input content is empty.")
        if len(content) == 1 and "no such user" not in content[0]:
            self.data = int(content[0])
