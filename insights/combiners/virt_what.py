"""
VirtWhat
========

Combiner to check if the host is running on a virtual or physical machine.  It
uses the results of the ``DMIDecode`` and ``VirtWhat`` parsers.  Prefer
``VirtWhat`` to ``DMIDecode``.

Examples:
    >>> vw = shared[VirtWhat]
    >>> vw.is_virtual
    True
    >>> vw.is_physical
    False
    >>> vw.generic
    'kvm'
    >>> 'aws' in vw
    False
"""

from insights.core.plugins import combiner
from insights.parsers.dmidecode import DMIDecode
from insights.parsers.virt_what import VirtWhat as VW, BAREMETAL

# Below 2 Maps are only For DMIDecode
GENERIC_MAP = {
    'vmware': ['VMware'],
    'kvm': ['Red Hat', 'KVM'],
    'xen': ['Xen', 'domU'],
    'virtualpc': ['Microsoft Corporation', 'Virtual Machine'],
    'virtualbox': ['innotek GmbH'],
    'parallels': ['Parallels'],
    'qemu': ['QEMU'],
}

SPECIFIC_MAP = {
    'aws': ['amazon'],
    'xen-hvm': ['HVM'],
}


@combiner([DMIDecode, VW])
class VirtWhat(object):
    """
    A combiner for checking if this machine is virtual or physical by checking
    ``virt-what`` or ``dmidecode`` command.

    Prefer ``virt-what`` to ``dmidecode``

    Attributes:
        is_virtual (bool): It's running in a virtual machine?
        is_physical (bool): It's running in a physical machine?
        generic (str): The type of the virtual machine. 'baremetal' if physical machine.
        specifics (list): List of the specific information.
    """

    def __init__(self, dmi, vw):
        self.is_virtual = self.is_physical = None
        self.generic = ''
        self.specifics = []

        if vw and not vw.errors:
            self.is_physical = vw.is_physical
            self.is_virtual = vw.is_virtual
            self.generic = vw.generic
            self.specifics = vw.specifics

        # Error occurred in ``virt-what``, try ``dmidecode``
        if (vw is None or vw.errors) and dmi:
            sys_info = dmi.get("system_information", [{}])[0]
            bios_info = dmi.get("bios_information", [{}])[0]
            dmi_info = list(sys_info.values()) + list(bios_info.values())
            if dmi_info:
                for dmi_v in dmi_info:
                    if not self.generic:
                        generic = [g for g, val in GENERIC_MAP.items() if any(v in dmi_v for v in val)]
                        self.generic = generic[0] if generic else ''
                    self.specifics.extend([g for g, val in SPECIFIC_MAP.items() if any(v in dmi_v for v in val)])

                self.is_virtual = True
                self.is_physical = False
                if self.generic == '':
                    self.generic = BAREMETAL
                    self.is_virtual = False
                    self.is_physical = True

    def __contains__(self, name):
        """bool: Is this ``name`` found in the specific list?"""
        return name in [self.generic] + self.specifics
