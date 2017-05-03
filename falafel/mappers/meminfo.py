from .. import Mapper, mapper, get_active_lines


class SubMemInfo(object):

    sub_keys = []

    def __init__(self, data):
        sub_dict = {sk: data.get(k) for k, sk in self.sub_keys}
        self.data = sub_dict
        for k, v in sub_dict.iteritems():
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


@mapper("meminfo")
class MemInfo(Mapper):
    """
    Meminfo field names are wildly inconsistent (imho).  This class attempts to
    bring a bit of order to the chaos.  All values are in bytes.

    KB describing /proc/meminfo:
    https://access.redhat.com/solutions/406773
    """

    VALUE_IN_BYTES = [
        "hugepages_total", "hugepages_free", "hugepages_reserved", "hugepages_surp"
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
        for name, cls in sub_classes.iteritems():
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
