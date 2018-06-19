"""
The entry for user foreman in passwd
====================================
This command shows the entry for only the user foreman in the /etc/passwd file

Typical output of ``/bin/grep  '^foreman:' /etc/passwd`` command is::

    foreman:x:990:983:Foreman:/usr/share/foreman:/bin/false

Examples:
    >>> passwd_foreman.data
    ['foreman', 'x', '990', '983', 'Foreman', '/usr/share/foreman', '/bin/false']

"""


from .. import Parser
from .. import parser
from ..specs import Specs


@parser(Specs.passwd_foreman)
class PasswdForeman(Parser):
    """
    Parse data from the ``/bin/grep  '^foreman:' /etc/passwd`` command.
    """

    def parse_content(self, content):
        if len(content) == 1 and content[0].startswith('foreman:'):
            self.data = content[0].split(':')
