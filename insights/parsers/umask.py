"""
Umask - command ``/usr/bin/umask -S``
=====================================
Parse the content of ``/usr/bin/umask -S`` command.

Sample ``/usr/bin/umask -S`` command output::

    u=rwx,g=rx,o=rx

Examples:

    >>> type(umask_obj)
    <class 'insights.parsers.umask.Umask'>
    >>> umask_obj['user']
    'rwx'
    >>> umask_obj['group']
    'rx'
    >>> umask_obj['other']
    'rx'
"""

from insights import Parser, parser
from insights.parsers import SkipException
from insights.specs import Specs


@parser(Specs.umask)
class Umask(Parser, dict):
    """Parse output of ``/usr/bin/umask -S`` command"""
    def parse_content(self, content):
        if not content:
            raise SkipException("No Contents")
        split_result = content[0].split(',')
        self['user'] = split_result[0].split('=')[1].strip()
        self['group'] = split_result[1].split('=')[1].strip()
        self['other'] = split_result[2].split('=')[1].strip()
