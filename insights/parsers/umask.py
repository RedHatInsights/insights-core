"""
Umask - command ``/usr/bin/umask``
==================================
The ``Umask`` class implements the parsing of ``/usr/bin/umask``
command, which is the value of default system umask.
"""

from insights import Parser, parser
from insights.parsers import SkipException
from insights.specs import Specs


@parser(Specs.umask)
class Umask(Parser, dict):
    """
    Parser for ``/usr/bin/umask`` file.

    Sample input is provided in the *Examples*.

    Sample content::

        0022

    Examples:

        >>> type(umask_obj)
        <class 'insights.parsers.umask.Umask'>
        >>> umask_obj['value']
        '0022'


    Resultant Data::

        "0022"

    Raises:
        SkipException: When contents are empty or invalid

    """

    def parse_content(self, content):

        if not content:
            raise SkipException("No Contents")

        if len(content) == 1 and content[0].isdigit():
            self['value'] = content[0]
        else:
            raise SkipException("No Valid Contents")
