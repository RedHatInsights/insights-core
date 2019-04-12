"""
NVMeCoreIOTimeout - The timeout for I/O operations submitted to NVMe devices
============================================================================

This parser reads the content of ``/sys/module/nvme_core/parameters/io_timeout``.
"""

from insights import Parser, parser
from insights.specs import Specs
from ..parsers import SkipException, ParseException


@parser(Specs.nvme_core_io_timeout)
class NVMeCoreIOTimeout(Parser):
    """
    Class for parsing the content of the ``/sys/module/nvme_core/parameters/io_timeout``.

    A typical sample of the content of this file looks like::

        4294967295

    Raises:
        SkipException: When content is empty or no parse-able content.
        ParseException: When type cannot be recognized.

    Attributes:
        val (int): It is used to show the current value of the timeout for I/O operations submitted to NVMe devices.

    Examples:
        >>> nciotmo.val
        4294967295
    """

    def parse_content(self, content):
        if not content or len(content) != 1:
            raise SkipException()
        if not content[0].strip('').isdigit():
            raise ParseException("Unexpected content: ", content)
        self.val = int(content[0].strip())
