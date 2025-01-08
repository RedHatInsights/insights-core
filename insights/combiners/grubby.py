"""
Grubby
======

Combiner for command ``/usr/sbin/grubby`` parsers.

This combiner uses the parsers:
:class:`insights.parsers.grubby.GrubbyDefaultIndex`,
:class:`insights.parsers.grubby.GrubbyInfoAll`.
"""

from insights.core.exceptions import ParseException
from insights.core.plugins import combiner
from insights.parsers.grubby import GrubbyDefaultIndex, GrubbyInfoAll


@combiner(GrubbyInfoAll, GrubbyDefaultIndex)
class Grubby(object):
    """
    Combine command "grubby" parsers into one Combiner.

    Attributes:
        boot_entries (dict): All boot entries indexed by the entry "index"
        default_index (int): the numeric index of the current default boot entry

    Raises:
        ParseException: when parsing into error.
    """
    def __init__(self, grubby_info_all, grubby_default_index):
        self.boot_entries = grubby_info_all.boot_entries
        self.default_index = grubby_default_index.default_index

    @property
    def default_boot_entry(self):
        if self.default_index not in self.boot_entries:
            raise ParseException("DEFAULT index %s not exist in parsed boot_entries: %s" %
                                    (self.default_index, list(self.boot_entries.keys())))
        return self.boot_entries[self.default_index]
