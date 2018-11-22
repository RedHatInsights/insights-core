"""
AvcCacheThreshold - File ``/sys/fs/selinux/avc/cache_threshold``
================================================================

This parser reads the content of ``/sys/fs/selinux/avc/cache_threshold``.
"""

from .. import parser, CommandParser

from ..parsers import ParseException
from insights.specs import Specs


@parser(Specs.avc_cache_threshold)
class AvcCacheThreshold(CommandParser):
    """
    Class ``AvcCacheThreshold`` parses the content of the ``/sys/fs/selinux/avc/cache_threshold``.

    Attributes:
        value (int): It is used to show the value of cache threshold.

    A small sample of the content of this file looks like::

        512

    Examples:
        >>> type(avc_cache_threshold)
        <class 'insights.parsers.avc_cache_threshold.AvcCacheThreshold'>
        >>> avc_cache_threshold.value
        512
    """

    def parse_content(self, content):
        if len(content) == 0 or len(content) > 1 or 'No such file or directory' in content[0]:
            raise ParseException("Error: ", content[0] if content else 'empty file')
        self.threshold_value = int(content[0].strip())

    @property
    def value(self):
        return self.threshold_value
