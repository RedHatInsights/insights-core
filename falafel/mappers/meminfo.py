from falafel.core.plugins import mapper
from falafel.core import MapperOutput, computed


class SubMemInfo(MapperOutput):

    sub_keys = []

    def __init__(self, data, path=None):
        sub_dict = {sk: data.get(k) for k, sk in self.sub_keys}
        self.data = sub_dict
        self.computed = {}
        for k in sub_dict:
            self._add_to_computed(k, sub_dict[k])
        self.compute()


class SwapMemInfo(SubMemInfo):

    sub_keys = [
        ("swaptotal", "total"),
        ("swapfree", "free"),
        ("swapcached", "cached")
    ]

    @computed
    def used(self):
        try:
            return self.total - self.free - self.cached
        except:
            pass


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

    @computed
    def using(self):
        return bool(self.total)

    @computed
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


class MemInfo(MapperOutput):
    """
    Meminfo field names are wildly inconsistent (imho).  This class attempts to
    bring a bit of order to the chaos.  All values are in bytes.

    KB describing /proc/meminfo:
    https://access.redhat.com/solutions/406773
    """

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

    def __init__(self, data, path=None):
        super(MemInfo, self).__init__(data)
        sub_classes = {
            "anon": AnonMemInfo(data),
            "file": FileMemInfo(data),
            "swap": SwapMemInfo(data),
            "slab": SlabMemInfo(data),
            "huge_pages": HugePageMemInfo(data),
            "commit": CommitMemInfo(data),
            "vmalloc": VmallocMemInfo(data),
            "cma": CmaMemInfo(data),
            "direct_map": DirectMapMemInfo(data)
        }
        for name, cls in sub_classes.iteritems():
            self._add_to_computed(name, cls)
        for meminfo_key, k in self.mem_keys:
            self._add_to_computed(k, self.data.get(meminfo_key))

    @computed
    def used(self):
        try:
            return self.total - self.free
        except:
            pass

    def get(self, key):
        try:
            self.__getitem__(key)
        except KeyError:
            pass

    def __getitem__(self, key):
        return super(MemInfo, self).__getitem__(key.lower())

VALUE_IN_BYTES = [
    "hugepages_total", "hugepages_free", "hugepages_reserved", "hugepages_surp"
]


@mapper('meminfo')
def meminfo(context):
    mem_info = {}
    for line in context.content:
        if line.strip():
            (key, value) = line.split(':', 1)
            # Store values as byte count
            key = key.strip().lower()
            if key in VALUE_IN_BYTES:
                mem_info[key.strip().lower()] = int(value.split()[0])
            else:
                mem_info[key.strip().lower()] = int(value.split()[0]) * 1024
    return MemInfo(mem_info)
