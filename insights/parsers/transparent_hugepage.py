"""
transparent_hugepage sysfs settings
===================================

Module for parsing the sysfs settings for transparent_hugepage:

ThpUseZeroPage - file ``/sys/kernel/mm/transparent_hugepage/use_zero_page``
---------------------------------------------------------------------------

Gets the contents of /sys/kernel/mm/transparent_hugepage/use_zero_page, which is either 0 or 1.

Sample input::

    0

Examples:

    >>> shared[ThpUseZeroPage].use_zero_page
    0


ThpEnabled - file ``/sys/kernel/mm/transparent_hugepage/enabled``
-----------------------------------------------------------------

Gets the contents of  /sys/kernel/mm/transparent_hugepage/enabled, which is something like
`always [madvise] never` where the active value is in brackets.

If no option is active (that should never happen), `get_opt()` will return None.

Sample input::

    always [madvise] never

Examples:

    >>> shared[ThpEnabled].line()
    always [madvise] never
    >>> shared[ThpEnabled].active_option
    madvise

"""

from .. import Parser, parser


@parser("thp_use_zero_page")
class ThpUseZeroPage(Parser):
    """
    Gets the contents of /sys/kernel/mm/transparent_hugepage/use_zero_page, which is either 0 or 1.
    """
    def parse_content(self, content):
        self.use_zero_page = " ".join(content).strip()


@parser("thp_enabled")
class ThpEnabled(Parser):
    """
    Gets the contents of  /sys/kernel/mm/transparent_hugepage/enabled, which is something like
    `always [madvise] never` where the active value is in brackets.
    If no option is active (that should never happen), get_opt() will return None.
    """
    def parse_content(self, content):
        self.line = " ".join(content).strip()
        self.active_option = None
        for w in self.line.split():
            if w.startswith("[") and w.endswith("]"):
                self.active_option = w[1:-1]
