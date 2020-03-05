# -*- coding: UTF-8 -*-

"""
AbrtStatusBare - command ``/usr/bin/abrt status --bare=True``
=============================================================

``/usr/bin/abrt status --bare=True`` returns the number of problems ABRT
detected in the system.

Examples:
    >>> abrt_status_bare.problem_count
    1997
"""

from insights import CommandParser, parser
from insights.specs import Specs


@parser(Specs.abrt_status_bare)
class AbrtStatusBare(CommandParser):
    """
    Parser for the output of ``abrt status --bare=True``

    Attributes:
        problem_count (int): the number of problems ABRT detected
    """
    def parse_content(self, content):
        self.problem_count = int(content[0].strip())
