"""
LruGenEnabled - file ``/sys/kernel/mm/lru_gen/enabled``
=======================================================

Parser to parse the output of file ``/sys/kernel/mm/lru_gen/enabled``
"""

from insights.core import Parser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.lru_gen_enabled)
class LruGenEnabled(Parser):
    """
    The parser for  ``/sys/kernel/mm/lru_gen/enabled`` file.

    The content of ``/sys/kernel/mm/lru_gen/enabled`` file is a hexadecimal number.
    Values , Feature
    ----------------
    0x0000, the multi-gen LRU feature is disabled
    0x0001, the multi-gen LRU feture is enabled
    0x0002, the feature of clearing the accessed bit in leaf page table entries in large batches is enabled
    0x0004, the feature of clearing the accessed bit in non-leaf page table entries as well is enabled
    0x0007, all the features are enabled

    Sample Content::
        0x0004

    Examples:
        >>> type(lru_gen_enabled)
        <class 'insights.parsers.lru_gen_enabled.LruGenEnabled'>
        >>> lru_gen_enabled.enabled
        True
        >>> lru_gen_enabled.features
        4

    Attributes:
        enabled (bool): False means multi-gen LRU feature is disabled,
            otherwise, any of feature is enabled.
        features (int): when enabled is True, checking the features to see
            which features are enabled.

    Raises:
        ParseException: When running into an unparsable line.
        SkipComponent: When file content is empty or has multiple lines.

    """

    def parse_content(self, content):
        if len(content) != 1:
            raise SkipComponent("Input content should only contain one line")

        if not content[0].startswith("0x"):
            raise ParseException("Input content is not a hex number")

        try:
            features = int(content[0], 16)
        except:
            raise ParseException("Input content is not a hex number")

        self.features = features
        self.enabled = features > 0
