"""
AvcCacheThreshold - File ``/sys/fs/selinux/avc/cache_threshold``
================================================================

This parser reads the content of ``/sys/fs/selinux/avc/cache_threshold``.
"""
from insights.core import CommandParser
from insights.core.exceptions import ParseException
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.avc_cache_threshold)
class AvcCacheThreshold(CommandParser):
    """
    Class ``AvcCacheThreshold`` parses the content of the ``/sys/fs/selinux/avc/cache_threshold``.

    Attributes:
        cache_threshold (int): It is used to show the value of cache threshold.

    A typical sample of the content of this file looks like::

        512

    Examples:
        >>> type(avc_cache_threshold)
        <class 'insights.parsers.avc_cache_threshold.AvcCacheThreshold'>
        >>> avc_cache_threshold.cache_threshold
        512
    """

    def parse_content(self, content):
        if len(content) != 1:
            raise ParseException("Error: ", content[0] if content else 'empty file')
        self.cache_threshold = int(content[0].strip())
