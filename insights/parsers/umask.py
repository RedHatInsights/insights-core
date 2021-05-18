"""
Umask - command ``/usr/bin/umask -S``
=====================================
This parser parses the output of ``/usr/bin/umask -S`` command.
"""

from insights import CommandParser, parser
from insights.parsers import SkipException
from insights.specs import Specs


@parser(Specs.umask)
class Umask(CommandParser):
    """
    Class for parsing the output of ``/usr/bin/umask -S`` command.

    Sample ``/usr/bin/umask -S`` command output::

        u=rwx,g=rx,o=rx

    Attributes:
        user (str): The default user permission of the created file
        group (str): The default group permission of the created file
        other (str): The default other permission of the created file
        raw (str): The raw value of the command output

    Examples:

        >>> type(umask_obj)
        <class 'insights.parsers.umask.Umask'>
        >>> umask_obj.user
        'rwx'
        >>> umask_obj.group
        'rx'
        >>> umask_obj.other
        'rx'
        >>> umask_obj.raw
        'u=rwx,g=rx,o=rx'
    """
    def parse_content(self, content):
        """Parse output of ``/usr/bin/umask -S`` command"""
        if not content:
            raise SkipException("No Contents")
        split_result = content[0].split(',')
        self.raw = content[0]
        self.user = split_result[0].split('=')[1].strip()
        self.group = split_result[1].split('=')[1].strip()
        self.other = split_result[2].split('=')[1].strip()
