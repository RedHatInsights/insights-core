"""
Parsers for file ``/sys/kernel/debug/x86/*_enabled`` outputs
============================================================

This module provides the following parsers:

X86PTIEnabled - file ``/sys/kernel/debug/x86/pti_enabled``
-----------------------------------------------------------

X86IBPBEnabled - file ``/sys/kernel/debug/x86/ibpb_enabled``
------------------------------------------------------------

X86IBRSEnabled - file ``/sys/kernel/debug/x86/ibrs_enabled``
------------------------------------------------------------

X86RETPEnabled - file ``/sys/kernel/debug/x86/retp_enabled``
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


@parser(Specs.x86_ibrs_enabled)
class X86IBRSEnabled(X86DebugEnabled):
    """
    Class for parsing file ``/sys/kernel/debug/x86/ibrs_enabled``

    Attributes:
        value (int): the result parsed of '/sys/kernel/debug/x86/ibrs_enabled'

    Raises:
        SkipException: When input content is empty
        ParseException: When input content is not available to parse
    """
    pass


@parser(Specs.x86_pti_enabled)
class X86PTIEnabled(X86DebugEnabled):
    """
    Class for parsing file ``/sys/kernel/debug/x86/pti_enabled``

    Attributes:
        value (int): the result parsed of '/sys/kernel/debug/x86/pti_enabled'

    Raises:
        SkipException: When input content is empty
        ParseException: When input content is not available to parse
    """
    pass


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
