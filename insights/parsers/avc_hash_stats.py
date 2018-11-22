"""
AvcHashStats - File ``/sys/fs/selinux/avc/hash_stats``
======================================================

This parser reads the content of ``/sys/fs/selinux/avc/hash_stats``.
"""

from .. import parser, CommandParser

from ..parsers import get_active_lines
from insights.specs import Specs


@parser(Specs.avc_hash_stats)
class AvcHashStats(CommandParser):
    """
    Class ``AvcHashStats`` parses the content of the ``/sys/fs/selinux/avc/hash_stats``.

    Attributes:
        entries (int): It is used to show the count of avc hash entries.
        buckets (int): It is used to show the total count of buckets.
        buckets_used (int): It is used to show the count of used buckets.
        longest_chain (int): It is used to show the longest chain.

    A small sample of the content of this file looks like::

        entries: 509
        buckets used: 290/512
        longest chain: 7


    Examples:
        >>> type(avc_hash_stats)
        <class 'insights.parsers.avc_hash_stats.AvcHashStats'>
        >>> avc_hash_stats.entries
        509
        >>> avc_hash_stats.buckets
        512
        >>> avc_hash_stats.buckets_used
        290
        >>> avc_hash_stats.longest_chain
        7
    """

    def parse_content(self, content):
        hash_stats_dict = {}
        for line in get_active_lines(content):
            key, value = map(lambda x: x.strip(), line.split(':'))
            if key not in hash_stats_dict:
                hash_stats_dict[key] = value
        self.hash_stats_dict = hash_stats_dict
        self.entries = int(hash_stats_dict['entries']) if hash_stats_dict.get('entries') else None
        self.buckets_used, self.buckets = map(lambda x: int(x.strip()),
                                              hash_stats_dict['buckets used'].split('/')) \
            if hash_stats_dict.get('buckets used') else [None, None]
        self.longest_chain = int(hash_stats_dict['longest chain']) if hash_stats_dict.get('longest chain') else None
