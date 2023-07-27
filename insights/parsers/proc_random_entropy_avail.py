"""
RandomEntropyAvail - File ``/proc/sys/kernel/random/entropy_avail``
===================================================================

Parser for parsing the ``/proc/sys/kernel/random/entropy_avail`` file.
"""

from insights.core import Parser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.random_entropy_avail)
class RandomEntropyAvail(Parser):
    """
    Class for parsing the ``/proc/sys/kernel/random/entropy_avail`` file.

    Sample input::

        3137

    Attributes:
        avail_entropy (int): the available entropy

    Examples:
        >>> type(random_entropy_obj)
        <class 'insights.parsers.proc_random_entropy_avail.RandomEntropyAvail'>
        >>> random_entropy_obj.avail_entropy
        3137

    Raises:
        SkipComponent: when there is no expected content in the file
    """

    def parse_content(self, content):
        if len(content) == 1 and content[0].isdigit():
            self.avail_entropy = int(content[0])
        if not hasattr(self, 'avail_entropy'):
            raise SkipComponent('No exptected available entropy value found')
