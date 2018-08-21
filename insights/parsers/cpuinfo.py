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
    flags           : fpu vme de pse tsc msr pae mce
    address sizes   : 40 bits physical, 48 bits virtual

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
    flags           : fpu vme de pse tsc msr pae mce
    address sizes   : 40 bits physical, 48 bits virtual

Examples:

    >>> cpu_info = shared[CpuInfo]
    >>> cpu_info.cpu_count
    2
    >>> cpu_info.socket_count
    2
    >>> cpu_info.vendor
    "GenuineIntel"
    >>> "fpu" in cpu_info.flags
    True
    >>> cpu_info.model_name
    "Intel(R) Xeon(R) CPU E5-2690 0 @ 2.90GHz"
    >>> cpu_info.get_processor_by_index(0)
    {
        "cpus": "0",
        "sockets": "0",
        "vendors": "GenuineIntel",
        "models": "Intel(R) Xeon(R) CPU E5-2690 0 @ 2.90GHz",
        "model_ids": "45",
        "families": "6",
        "flags": "fpu vme de pse tsc msr pae mce",
        "clockspeeds": "2900.000",
        "cache_sizes": "20480 KB"
        "cpu_cores": "1"
    }


"""

from collections import defaultdict
from .. import Parser, parser, defaults, get_active_lines, LegacyItemAccess
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
        address sizes   : 40 bits physical, 48 bits virtual

    The following keys would be lists of:

    * **cpus** - the *processor* line (e.g. ``1``)
    * **sockets** - the *physical id* line (e.g. ``2``)
    * **vendors** - the *vendor_id* line (e.g. ``GenuineIntel``)
    * **models** - the *models name* line (e.g. ``Intel(R) Xeon(R) CPU E5-2690 0 @ 2.90GHz``)
    * **model_ids** - the *model* line (e.g. ``45``)
    * **families** - the *cpu family* line (e.g. ``6``)
    * **clockspeeds** - the *cpu MHz* line (e.g. ``2900.000``)
    * **cache_sizes** - the *cache size* line (e.g. ``20480 KB``)
    * **cpu_cores** - the *cpu cores* line (e.g. ``1``)
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
            "flags": "flags"
        }

        for line in get_active_lines(content, comment_char="COMMAND>"):
            key, value = [p.strip() for p in line.split(":", 1)]
            if key in mappings:
                self.data[mappings[key]].append(value)

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
    @defaults()
    def cpu_count(self):
        """
        str: Returns the number of CPUs.
        """
        return len(self.data.get("cpus", []))

    @property
    @defaults()
    def socket_count(self):
        """
        str: Returns the number of sockets.  This is distinct from the number
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
    @defaults()
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
    def core_total(self):
        """
        str: Returns the total number of cores for the server if available, else None.
        """
        if self.data and 'cpu_cores' in self.data:
            return sum([int(c) for c in self.data['cpu_cores']])
        else:
            return None

    def get_processor_by_index(self, index):
        """
        Construct a dictionary of the information stored for the given CPU.

        Parameters:
            index (int): The CPU index to retrieve.

        Returns:
            dict: A dictionary of the information for that CPU.
        """
        return dict((k, v[index]) for k, v in self.data.items())
