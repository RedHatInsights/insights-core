"""
CpuInfo - file ``/proc/cpuinfo``
================================

This parser reads the content of the ``/proc/cpuinfo`` file and parses it
into a dictionary of lists, keyed on the left hand column of the cpuinfo
output.

The object also provides properties for the standard information about the
CPU and motherboard architecture.

Sample input::

    processor       : 0
    vendor_id       : GenuineIntel
    cpu family      : 6
    model           : 45
    model name      : Intel(R) Xeon(R) CPU E5-2690 0 @ 2.90GHz
    stepping        : 2
    microcode       : 1808
    cpu MHz         : 2900.000
    cache size      : 20480 KB
    physical id     : 0
    siblings        : 1
    core id         : 0
    cpu cores       : 1
    apicid          : 0
    flags           : fpu vme de pse tsc msr pae mce
    address sizes   : 40 bits physical, 48 bits virtual
    bugs            : cpu_meltdown spectre_v1 spectre_v2 spec_store_bypass l1tf mds swapgs taa itlb_multihit

    processor       : 1
    vendor_id       : GenuineIntel
    cpu family      : 6
    model           : 45
    model name      : Intel(R) Xeon(R) CPU E5-2690 0 @ 2.90GHz
    stepping        : 2
    microcode       : 1808
    cpu MHz         : 2900.000
    cache size      : 20480 KB
    physical id     : 2
    siblings        : 1
    core id         : 0
    cpu cores       : 1
    apicid          : 2
    flags           : fpu vme de pse tsc msr pae mce
    address sizes   : 40 bits physical, 48 bits virtual
    bugs            : cpu_meltdown spectre_v1 spectre_v2 spec_store_bypass l1tf mds swapgs taa itlb_multihit

Examples:

    >>> cpu_info.cpu_count
    2
    >>> sorted(cpu_info.apicid)
    ['0', '2']
    >>> cpu_info.socket_count
    2
    >>> cpu_info.vendor
    'GenuineIntel'
    >>> "fpu" in cpu_info.flags
    True
    >>> cpu_info.model_name
    'Intel(R) Xeon(R) CPU E5-2690 0 @ 2.90GHz'
    >>> cpu_info.get_processor_by_index(0)['cpus']
    '0'
    >>> cpu_info.get_processor_by_index(0)['vendors']
    'GenuineIntel'
    >>> cpu_info.microcode
    '1808'
"""
import warnings

from collections import defaultdict
from insights import Parser, parser, defaults, get_active_lines, LegacyItemAccess
from insights.specs import Specs


@parser(Specs.cpuinfo)
class CpuInfo(LegacyItemAccess, Parser):
    """
    CpuInfo parser - able to be used as a dictionary through the
    LegacyItemAccess mixin class.

    The following items are remapped into lists, with the element number
    corresponding to the CPU.  For example, given the following input::

        processor       : 1
        vendor_id       : GenuineIntel
        cpu family      : 6
        model           : 45
        model name      : Intel(R) Xeon(R) CPU E5-2690 0 @ 2.90GHz
        stepping        : 2
        microcode       : 1808
        cpu MHz         : 2900.000
        cache size      : 20480 KB
        physical id     : 2
        siblings        : 1
        core id         : 0
        cpu cores       : 1
        apicid          : 2
        address sizes   : 40 bits physical, 48 bits virtual
        bugs            : cpu_meltdown spectre_v1 spectre_v2 spec_store_bypass l1tf mds swapgs taa itlb_multihit

    The following keys would be lists of:

    * **cpus** - the *processor* line (e.g. ``1``)
    * **sockets** - the *physical id* line (e.g. ``2``)
    * **vendors** - the *vendor_id* line (e.g. ``GenuineIntel``)
    * **models** - the *model name* line (e.g. ``Intel(R) Xeon(R) CPU E5-2690 0 @ 2.90GHz``)
    * **model_ids** - the *model* line (e.g. ``45``)
    * **families** - the *cpu family* line (e.g. ``6``)
    * **clockspeeds** - the *cpu MHz* line (e.g. ``2900.000``)
    * **cache_sizes** - the *cache size* line (e.g. ``20480 KB``)
    * **cpu_cores** - the *cpu cores* line (e.g. ``1``)
    * **apicid** - the *apicid* line (e.g. ``1``)
    * **stepping** - the *stepping* line (e.g. ``2``)
    * **address_sizes** - the *address sizes* line (e.g. ``40 bits physical, 48 bits virtual``)
    * **bugs** - the *bugs* line (e.g. ``cpu_meltdown spectre_v1 spectre_v2 spec_store_bypass l1tf mds swapgs taa itlb_multihit``)
    """

    def parse_content(self, content):

        self.data = defaultdict(list)
        mappings = {
            "processor": "cpus",
            "physical id": "sockets",
            "vendor_id": "vendors",
            "model name": "models",
            "model": "model_ids",
            "cpu family": "families",
            "cpu MHz": "clockspeeds",
            "cache size": "cache_sizes",
            "cpu cores": "cpu_cores",
            "apicid": "apicid",
            "flags": "flags",
            "stepping": "stepping",
            "Features": "features",
            "CPU implementer": "cpu_implementer",
            "CPU architecture": "cpu_architecture",
            "CPU variant": "cpu_variant",
            "CPU part": "cpu_part",
            "CPU revision": "cpu_revision",
            "cpu": "cpu",
            "revision": "revision",
            "address sizes": "address_sizes",
            "bugs": "bugs",
            "microcode": "microcode",
            "cpu MHz static": "clockspeeds",
            "features": "features"
        }

        for line in get_active_lines(content, comment_char="COMMAND>"):
            key, value = [p.strip() for p in line.split(":", 1)]
            # For s390x the : symbol is after the number instead of before.
            # So re-split and set the key and value before checking mappings.
            if key.startswith("processor") and key[-1].isdigit():
                key, value = key.split(" ", 1)

            if key in mappings:
                self.data[mappings[key]].append(value)

        if "cpu" in self.data and "POWER" in self.data["cpu"][0]:
            # this works differently than on x86 and is not per-cpu
            model_id = self.data["model_ids"][0]
            cpu_cnt = self.cpu_count
            self.data["model_ids"] = [model_id] * cpu_cnt

        # s390x cpuinfo is setup drastically differently than other arches.
        # It doesn't print the same information for each cpu, like other arches.
        # So any info not repeated per cpu, copy, delete and then add for each cpu entry.
        if "vendors" in self.data and "IBM/S390" in self.data["vendors"][0]:
            vendor = self.data["vendors"][0]
            features = self.data["features"][0]
            cpu_cnt = self.cpu_count
            self.data["vendors"] = [vendor] * cpu_cnt
            self.data["features"] = [features] * cpu_cnt

        self.data = dict(self.data)

    def __iter__(self):
        """
        Iterating through this object will yield the ``get_processor_by_index``
        information for each CPU.
        """
        for idx in range(len(self["cpus"])):
            yield self.get_processor_by_index(idx)

    @property
    @defaults()
    def cpu_speed(self):
        """
        str: Returns the CPU speed of the first CPU.
        """
        return self.data["clockspeeds"][0]

    @property
    @defaults()
    def cache_size(self):
        """
        str: Returns the cache size of the first CPU.
        """
        return self.data["cache_sizes"][0]

    @property
    def cpu_count(self):
        """
        int : Returns the number of CPUs.
        """
        return len(self.data.get("cpus", []))

    @property
    def apicid(self):
        """
        list: Returns the list of apicid of the processor.
        """
        return self.data.get("apicid", [])

    @property
    def socket_count(self):
        """
        int: Returns the number of sockets.  This is distinct from the number
        of CPUs.
        """
        return len(set(self.data.get("sockets", [])))

    @property
    @defaults()
    def model_name(self):
        """
        str: Returns the model name of the first CPU.
        """
        return self.data["models"][0]

    @property
    @defaults()
    def model_number(self):
        """
        str: Returns the model ID of the first CPU.
        """
        return self.data["model_ids"][0]

    @property
    @defaults([])
    def flags(self):
        """
        list: Returns a list of feature flags for the first CPU.
        """
        return self.data["flags"][0].split()

    @property
    @defaults()
    def vendor(self):
        """
        str: Returns the vendor of the first CPU.
        """
        return self.data["vendors"][0]

    @property
    @defaults()
    def microcode(self):
        """
        str: Returns the microcode of the first CPU.
        """
        return self.data["microcode"][0]

    @property
    @defaults()
    def core_total(self):
        """
        int: Returns the total number of cores for the server if available, else None.

        .. warning::
            This method is deprecated, and will be removed after 3.2.25. Please use
            :py:class:`insights.parsers.lscpu.LsCPU` class attribute
            ``info['Cores per socket']`` and ``info['Sockets']`` values instead.
        """
        warnings.warn("`is_hypervisor` is deprecated and will be removed after 3.2.25: Use `virt_what.VirtWhat` which uses the command `virt-what` to check the hypervisor type.", DeprecationWarning)
        if self.data and 'cpu_cores' in self.data:
            # I guess we can't get this fancey on older versions of RHEL
            # return sum({e['sockets']: int(e['cpu_cores']) for e in self}.values())
            physical_dict = {}
            for e in self:
                # we should rename sockets here to physical_ids as cpuinfo
                # has it there can be many physical_ids per socket
                # see fgrep 'physical id' /proc/cpuinfo on a single
                # package system
                physical_dict[e['sockets']] = int(e['cpu_cores'])
            return sum(physical_dict.values())

    def get_processor_by_index(self, index):
        """
        Construct a dictionary of the information stored for the given CPU.

        Parameters:
            index (int): The CPU index to retrieve.

        Returns:
            dict: A dictionary of the information for that CPU.
        """
        return dict((k, v[index]) for k, v in self.data.items())
