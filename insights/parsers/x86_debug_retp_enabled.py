"""
Parsers for file ``/sys/kernel/debug/x86/retp_enabled`` outputs
============================================================

This module provides the following parsers:

X86IBPBEnabled - file ``/sys/kernel/debug/x86/retp_enabled``
------------------------------------------------------------
"""

from insights import parser
from insights.specs import Specs
from insights.parsers.x86_debug_enabled import X86DebugEnabled


@parser(Specs.x86_retp_enabled)
class X86RETPEnabled(X86DebugEnabled):
    """
    Class for parsing file ``/sys/kernel/debug/x86/retp_enabled``

    Attributes:
        value (int): the result parsed of '/sys/kernel/debug/x86/retp_enabled'

    Raises:
        SkipException: When input content is empty
        ParseException: When input content is not available to parse
    """
    pass
