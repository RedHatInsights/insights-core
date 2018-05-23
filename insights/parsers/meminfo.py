"""
meminfo - file ``/proc/meminfo``
================================

This suite of parsers deals with various parts of the contents of
``/proc/meminfo``.  They store the data for many different groupings of
memory usage information as key-value pairs and attributes.  Key strings are
converted to lower case, and all values are stored as integers.  Data stored
in kilobytes (i.e. everything but the hugepage values) are converted to bytes
by multiplying by 1024.

All keys are stored in the parser class as properties.  The information
relevant to particular uses of memory are also available in the following
properties:

``swap``: for swap related information:

* ``total`` - the *SwapTotal* information
* ``free`` - the *SwapFree* information
* ``cached`` - the *SwapCached* information
* ``used`` - total - (free + cached)

``anon``: for anonymous page information:

* ``active`` - the *Active(anon)* information
* ``inactive`` - the *Inactive(anon)* information
* ``pages`` - the *AnonPages* information

``file``: for file mapping information:

* ``active`` - the *Active(file)* information
* ``inactive`` - the *Inactive(file)* information

``slab``: for SLAB allocator information:

* ``total`` - the *Slab* information
* ``reclaimable`` - the *SReclaimable* information
* ``unreclaimable`` - the *SUnreclaim* information

``huge_pages``: for HugePage allocator information:

* ``total`` - the *Hugepages_Total* information
* ``free`` - the *Hugepages_Free* information
* ``reserved`` - the *Hugepages_Rsvd* information
* ``surplus`` - the *Hugepages_Surp* information
* ``size`` - the *HugepageSize* information
* ``anon`` - the *AnonHugepages* information

``huge_pages`` also contains two properties to help parsers determine whether
huge pages are in use:

* ``using`` - are huge pages in use?  Is *Hugepages_Total* > 0?
* ``using_transparent`` - are transparent huge pages in use?  Is
  *AnonHugePages* > 0?


``commit``: for memory overcommit information:

* ``total`` - the *Committed_As* information
* ``limit`` - the *CommitLimit* information

``vmalloc``: for virtual memory allocation information:

* ``total`` - the *VMAllocTotal* information
* ``used`` - the *VMAllocUsed* information
* ``chunk`` - the *VMAllocChunk* information

``cma``: the CMA information:

* ``total`` - the *CMAllocTotal* information
* ``free`` - the *CMAllocFree* information

``direct_map``: the direct memory map information

* ``kb`` - the *DirectMap4K* information
* ``mb`` - the *DirectMap2M* information
* ``gb`` - the *DirectMap1G* information

Sample data::

    MemTotal:        8009912 kB
    MemFree:          538760 kB
    MemAvailable:    6820236 kB
    Buffers:          157048 kB
    Cached:          4893932 kB
    SwapCached:          120 kB
    Active:          2841500 kB
    Inactive:        2565560 kB
    Active(anon):     311596 kB
    Inactive(anon):   505800 kB
    Active(file):    2529904 kB
    Inactive(file):  2059760 kB
    ...

Examples:

    >>> mem = shared[MemInfo]
    >>> m.data.['memtotal'] # Old style accessor
    8202149888
    >>> mem.total # New property-based accessor
    8202149888
    >>> mem.used # Calculated
    7650459648
    >>> m.swap.total
    3221221376
    >>> m.swap.free
    3211624448
    >>> m.swap.used # Calculated
    9474048
"""

from .. import Parser, parser, get_active_lines
from insights.specs import Specs


class SubMemInfo(object):

    sub_keys = []

    def __init__(self, data):
        sub_dict = dict((sk, data.get(k)) for k, sk in self.sub_keys)
        self.data = sub_dict
        for k, v in sub_dict.items():
            setattr(self, k, v)


class SwapMemInfo(SubMemInfo):

    sub_keys = [
        ("swaptotal", "total"),
        ("swapfree", "free"),
        ("swapcached", "cached")
    ]

    @property
    def used(self):
        return self.total - self.free - self.cached


class AnonMemInfo(SubMemInfo):

    sub_keys = [
        ("active(anon)", "active"),
        ("inactive(anon)", "inactive"),
        ("anonpages", "pages")
    ]


class FileMemInfo(SubMemInfo):

    sub_keys = [
        ("active(file)", "active"),
        ("inactive(file)", "inactive")
    ]


class SlabMemInfo(SubMemInfo):

    sub_keys = [
        ("slab", "total"),
        ("sreclaimable", "reclaimable"),
        ("sunreclaim", "unreclaimable")
    ]


class HugePageMemInfo(SubMemInfo):

    sub_keys = [
        ("hugepages_total", "total"),
        ("hugepages_free", "free"),
        ("hugepages_rsvd", "reserved"),
        ("hugepages_surp", "surplus"),
        ("hugepagesize", "size"),
        ("anonhugepages", "anon")
    ]

    @property
    def using(self):
        return bool(self.total)

    @property
    def using_transparent(self):
        return bool(self.anon)


class CommitMemInfo(SubMemInfo):

    sub_keys = [
        ("committed_as", "total"),
        ("commitlimit", "limit")
    ]


class VmallocMemInfo(SubMemInfo):

    sub_keys = [
        ("vmalloctotal", "total"),
        ("vmallocused", "used"),
        ("vmallocchunk", "chunk")
    ]


class CmaMemInfo(SubMemInfo):

    sub_keys = [
        ("cmatotal", "total"),
        ("cmafree", "free")
    ]


class DirectMapMemInfo(SubMemInfo):

    sub_keys = [
        ("directmap4k", "kb"),
        ("directmap2m", "mb"),
        ("directmap1g", "gb")
    ]


@parser(Specs.meminfo)
class MemInfo(Parser):
    """
    Meminfo field names are wildly inconsistent (imho).  This class attempts to
    bring a bit of order to the chaos.  All values are in bytes.

    KB describing /proc/meminfo

    https://access.redhat.com/solutions/406773
    """

    VALUE_IN_BYTES = [
        "hugepages_total", "hugepages_free", "hugepages_rsvd", "hugepages_surp"
    ]

    mem_keys = [
        ("memtotal", "total"),
        ("memfree", "free"),
        ("memavailable", "available"),
        ("buffers", "buffers"),
        ("cached", "cached"),
        ("active", "active"),
        ("inactive", "inactive"),
        ("unevictable", "unevictable"),
        ("dirty", "dirty"),
        ("writeback", "writeback"),
        ("mapped", "mapped"),
        ("shmem", "shmem"),
        ("mlocked", "mlocked"),
        ("kernelstack", "kernel_stack"),
        ("pagetables", "page_tables"),
        ("nfs_unstable", "nfs_unstable"),
        ("bounce", "bounce"),
        ("writebacktmp", "writeback_tmp"),
        ("hardwarecorrupted", "corrupted"),
    ]

    def __init__(self, context):
        super(MemInfo, self).__init__(context)
        sub_classes = {
            "anon": AnonMemInfo(self.data),
            "file": FileMemInfo(self.data),
            "swap": SwapMemInfo(self.data),
            "slab": SlabMemInfo(self.data),
            "huge_pages": HugePageMemInfo(self.data),
            "commit": CommitMemInfo(self.data),
            "vmalloc": VmallocMemInfo(self.data),
            "cma": CmaMemInfo(self.data),
            "direct_map": DirectMapMemInfo(self.data)
        }
        for name, cls in sub_classes.items():
            setattr(self, name, cls)
        for meminfo_key, k in self.mem_keys:
            setattr(self, k, self.data.get(meminfo_key))

    def parse_content(self, content):
        self.data = {}
        for line in get_active_lines(content, comment_char="COMMAND>"):
            (key, value) = line.split(':', 1)
            # Store values as byte count
            key = key.strip().lower()
            if key in MemInfo.VALUE_IN_BYTES:
                self.data[key.strip().lower()] = int(value.split()[0])
            else:
                self.data[key.strip().lower()] = int(value.split()[0]) * 1024

    @property
    def used(self):
        return self.total - self.free
