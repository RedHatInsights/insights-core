"""
transparent_hugepage sysfs settings
===================================

Module for parsing the sysfs settings for transparent_hugepage:

ThpUseZeroPage - file ``/sys/kernel/mm/transparent_hugepage/use_zero_page``
---------------------------------------------------------------------------

ThpEnabled - file ``/sys/kernel/mm/transparent_hugepage/enabled``
-----------------------------------------------------------------

ThpShmemEnabled - file ``/sys/kernel/mm/transparent_hugepage/shmem_enabled``
----------------------------------------------------------------------------
"""

from .. import Parser, parser
from insights.core.exceptions import ParseException
from insights.specs import Specs


@parser(Specs.thp_use_zero_page)
class ThpUseZeroPage(Parser):
    """
    Gets the contents of /sys/kernel/mm/transparent_hugepage/use_zero_page, which is either 0 or 1.

    Attributes:
        use_zero_page (str): The setting, should be 0 or 1.

    Sample input::

        0

    Examples:
        >>> type(thp_use_zero_page)
        <class 'insights.parsers.transparent_hugepage.ThpUseZeroPage'>
        >>> thp_use_zero_page.use_zero_page
        '0'
    """
    def parse_content(self, content):
        self.use_zero_page = " ".join(content).strip()


@parser(Specs.thp_enabled)
class ThpEnabled(Parser):
    """
    Gets the contents of  /sys/kernel/mm/transparent_hugepage/enabled, which is something like
    `always [madvise] never` where the active value is in brackets.
    If no option is active (that should never happen), `active_option` will contain None.

    Attributes:
        line (str): Contents of the input file.
        active_option (str): The active option for transparent huge pages, or `None` if not present.

    Sample input::

        always [madvise] never

    Examples:
        >>> type(thp_enabled)
        <class 'insights.parsers.transparent_hugepage.ThpEnabled'>
        >>> thp_enabled.line
        'always [madvise] never'
        >>> thp_enabled.active_option
        'madvise'

    """
    def parse_content(self, content):
        self.line = " ".join(content).strip()
        self.active_option = None
        for w in self.line.split():
            if w.startswith("[") and w.endswith("]"):
                self.active_option = w[1:-1]


@parser(Specs.thp_shmem_enabled)
class ThpShmemEnabled(Parser):
    """
    Class for parsing the ``/sys/kernel/mm/transparent_hugepage/shmem_enabled`` files..

    Attributes:
        line (str): Contents of the input file.
        active_option (str): The active option for shmem_enabled of transparent huge pages, or `None` if not present.

    Typical content of the file is::

        always within_size advise [never] deny force

    Examples:
        >>> type(thp_shmem_enabled)
        <class 'insights.parsers.transparent_hugepage.ThpShmemEnabled'>
        >>> thp_shmem_enabled.line
        'always within_size advise [never] deny force'
        >>> thp_shmem_enabled.active_option
        'never'
    """
    def parse_content(self, content):
        self.line = " ".join(content).strip()
        self.active_option = None
        for w in self.line.split():
            if w.startswith("[") and w.endswith("]") and w[1:-1]:
                self.active_option = w[1:-1]
                break
        if not (self.line or self.active_option):
            raise ParseException('Error: {0}'.format(content or 'empty file'))
