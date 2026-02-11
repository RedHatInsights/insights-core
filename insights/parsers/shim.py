"""
Shim Entries
============

Parsers provided in this module includes:

StringsShimx64 - command ``strings /boot/efi/EFI/redhat/shimx64.efi``
---------------------------------------------------------------------
"""

from insights.core import TextFileOutput
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.strings_shimx64_efi)
class StringsShimx64(TextFileOutput):
    """
    Parse the output of the ``strings /boot/efi/EFI/redhat/shimx64.efi`` command.
    But the output is filtered.

    .. note::
        Please refer to its super-class :class:`insights.core.TextFileOutput` for more
        details.

    Sample output of this command::

        @.text
        `.reloc
        B/14
        @.data
        @.dynamic
        .rela
        @.sbat
        YZQR
        =g~
        Redmond1
        Microsoft Corporation1-0+
        $Microsoft Ireland Operations Limited1'0%
        nShield TSS ESN:3605-05E0-D9471%0#
        Microsoft Time-Stamp Service
        /?TGd
        ~0|1
        Washington1
        Redmond1
        Microsoft Corporation1&0$
        Microsoft Time-Stamp PCA 20100

    Examples:
        >>> from insights.core.filters import add_filter
        >>> from insights.specs import Specs
        >>> add_filter(Specs.strings_shimx64_efi, 'abc_def_af')
        >>> StringsShimx64.last_scan('abc_def_af_line', 'abc_def_af')
    """
