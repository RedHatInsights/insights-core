"""
VmaRaEnabledS390x - file ``/sys/kernel/mm/swap/vma_ra_enabled``
===============================================================

Parser to parse the output of file ``/sys/kernel/mm/swap/vma_ra_enabled``
"""
from insights.core import Parser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.vma_ra_enabled)
class VmaRaEnabledS390x(Parser):
    """
    Base class to parse ``/sys/kernel/mm/swap/vma_ra_enabled`` file,
    the file content will be stored in a string.

    Sample output for file::

        True

    Examples:
        >>> type(vma)
        <class 'insights.parsers.vma_ra_enabled_s390x.VmaRaEnabledS390x'>
        >>> vma.ra_enabled
        True

    Attributes:
        ra_enabled (bool): The result parsed

    Raises:
        SkipComponent: When file content is empty

    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent("Input content is empty")

        if content[0] == 'True':
            self.ra_enabled = True
        else:
            self.ra_enabled = False
