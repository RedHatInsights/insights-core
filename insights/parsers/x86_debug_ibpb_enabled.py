"""
Parsers for file ``/sys/kernel/debug/x86/ibpb_enabled`` outputs
============================================================

This module provides the following parsers:

X86IBPBEnabled - file ``/sys/kernel/debug/x86/ibpb_enabled``
------------------------------------------------------------
"""

from insights import parser
from insights.specs import Specs
from insights.parsers.x86_debug_enabled import X86DebugEnabled


@parser(Specs.x86_ibpb_enabled)
class X86IBPBEnabled(X86DebugEnabled):
    """
    Class for parsing file ``/sys/kernel/debug/x86/ibpb_enabled``

    Attributes:
        value (int): the result parsed of '/sys/kernel/debug/x86/ibpb_enabled'

    Raises:
        SkipException: When input content is empty
        ParseException: When input content is not available to parse
    """
    pass
