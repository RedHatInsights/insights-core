"""
Parsers to parse the output of ``modinfo <module_name>``
========================================================

ModInfoEach - Command ``modinfo *``
-----------------------------------
for any module listed by ``lsmod``

ModInfoAll - Command ``modinfo *(all modules)``
-----------------------------------------------
for all modules listed by ``lsmod``

KernelModulesInfo - Command ``modinfo filtered_modules``
--------------------------------------------------------
"""
from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs
from insights.util import deprecated


class ModInfo(dict):
    """
    Base class for the information about a kernel module, the module
    info will be stored in dictionary format. Besides of that, the following
    utility properties are provided as well.

    """
    @classmethod
    def from_content(cls, content):
        """
        A classmethod to generated a `ModInfo` object from the given `content`
        list. Two more keys `module_name` and `module_deps` will be created as
        well per the `content`.

        Raises:
            SkipComponent: When nothing need to check to a dict.
        """
        if not content:
            raise SkipComponent("No Contents")

        data = {}
        for line in content:
            line = line.strip()
            if ':' in line:
                key, value = [l.strip() for l in line.split(':', 1)]
                if key not in data:
                    data[key] = value
                else:
                    old_val = data[key]
                    data[key] = [old_val] if isinstance(old_val, str) else old_val
                    data[key].append(value)

        if not data:
            raise SkipComponent("No Parsed Contents")

        data['module_deps'] = list(data.get('depends', '').split(','))
        data['module_name'] = data.get('filename', '').rsplit('/')[-1].split('.')[0]

        return cls(data)

    @property
    def module_name(self):
        """
        (str): This will return kernel module name when set, else empty str.
        """
        return self.get('module_name', '')

    @property
    def module_path(self):
        """
        (str): This will return kernel module path when set, else `None`.
        """
        return self.get('filename', '')

    @property
    def module_deps(self):
        """
        (list): This will return the list of kernel modules depend on the kernel
                module when set, else `[]`.
        """
        return self.get('module_deps', [])

    @property
    def module_firmware(self):
        """
        (list): This will return the list of firmwares used by this module
                when set, else `[]`.
        """
        return self.get('firmware', [])

    @property
    def module_alias(self):
        """
        (list): This will return the list of alias to this kernel  module
                when set, else `[]`.
        """
        return self.get('alias', [])

    @property
    def module_parm(self):
        """
        (list): This will return the list of parms for this kernel module
                when set, else `[]`.
        """
        return self.get('parm', [])

    @property
    def module_version(self):
        """
        (str): This will return the kernel module version when set, else empty string.
        """
        return self.get('version', '')

    @property
    def module_signer(self):
        """
        (str): This will return the signer of kernel module when set, else empty string.
        """
        return self.get('signer', '')

    @property
    def module_details(self):
        """
        (dict): This will return the kernel module details when set.
        """
        return self


@parser(Specs.modinfo_filtered_modules)
class KernelModulesInfo(CommandParser, dict):
    """
    Class to parse the information about filtered kernel modules collected by
    "modinfo filtered_modules". The result will be stored in a dictionary.
    The key is the module name, the value is a instance of ModInfo with more
    details.

    Sample output::

        filename:       /lib/modules/3.10.0-957.10.1.el7.x86_64/kernel/drivers/net/vmxnet3/vmxnet3.ko.xz
        version:        1.4.14.0-k
        license:        GPL v2
        description:    VMware vmxnet3 virtual NIC driver
        author:         VMware, Inc.
        retpoline:      Y
        rhelversion:    7.6
        srcversion:     7E672688ACACBDD2E363B63
        alias:          pci:v000015ADd000007B0sv*sd*bc*sc*i*
        depends:
        intree:         Y
        vermagic:       3.10.0-957.10.1.el7.x86_64 SMP mod_unload modversions
        signer:         Red Hat Enterprise Linux kernel signing key
        sig_key:        A5:70:18:DF:B6:C9:D6:1F:CF:CE:0A:3D:02:8B:B3:69:BD:76:CA:ED
        sig_hashalgo:   sha256
        filename:       /lib/modules/3.10.0-993.el7.x86_64/kernel/drivers/net/ethernet/intel/i40e/i40e.ko.xz
        firmware:       i40e/i40e-e2-7.13.1.0.fw
        firmware:       i40e/i40e-e1h-7.13.1.0.fw
        version:        2.3.2-k
        license:        GPL
        description:    Intel(R) Ethernet Connection XL710 Network Driver
        author:         Intel Corporation, <e1000-devel@lists.sourceforge.net>
        retpoline:      Y
        rhelversion:    7.7
        srcversion:     DC5C250666ADD8603966656
        alias:          pci:v00008086d0000158Bsv*sd*bc*sc*i*
        alias:          pci:v00008086d0000158Asv*sd*bc*sc*i*
        depends:        ptp
        intree:         Y
        vermagic:       3.10.0-993.el7.x86_64 SMP mod_unload modversions
        signer:         Red Hat Enterprise Linux kernel signing key
        sig_key:        81:7C:CB:07:72:4E:7F:B8:15:24:10:F9:27:2D:AA:CF:80:3E:CE:59
        sig_hashalgo:   sha256
        parm:           debug:Debug level (0=none,...,16=all), Debug mask (0x8XXXXXXX) (uint)
        parm:           int_mode: Force interrupt mode other than MSI-X (1 INT#x; 2 MSI) (int)

    Raises:
        SkipComponent: When nothing need to parse.

    Examples:
        >>> from insights.core.filters import add_filter
        >>> from insights.specs import Specs
        >>> add_filter(Specs.modinfo_modules, 'i40e')
        >>> add_filter(Specs.modinfo_modules, 'vmxnet3')
        >>> type(mods_info)
        <class 'insights.parsers.modinfo.KernelModulesInfo'>
        >>> 'i40e' in mods_info
        True
        >>> mods_info['i40e'].module_version
        '2.3.2-k'
        >>> mods_info['i40e'].module_path
        '/lib/modules/3.10.0-993.el7.x86_64/kernel/drivers/net/ethernet/intel/i40e/i40e.ko.xz'
        >>> sorted(mods_info['i40e'].module_firmware)
        ['i40e/i40e-e1h-7.13.1.0.fw', 'i40e/i40e-e2-7.13.1.0.fw']
        >>> sorted(mods_info['i40e'].module_alias)
        ['pci:v00008086d0000158Asv*sd*bc*sc*i*', 'pci:v00008086d0000158Bsv*sd*bc*sc*i*']
        >>> sorted(mods_info['i40e'].module_parm)
        ['debug:Debug level (0=none,...,16=all), Debug mask (0x8XXXXXXX) (uint)', 'int_mode: Force interrupt mode other than MSI-X (1 INT#x; 2 MSI) (int)']
        >>> 'vmxnet3' in mods_info
        True

    Attributes:
        retpoline_y (set): A set of names of the modules with the attribute "retpoline: Y".
        retpoline_n (set): A set of names of the modules with the attribute "retpoline: N".
    """
    def parse_content(self, content):
        if (not content) or (not self.file_path):
            raise SkipComponent("No Contents")

        self.retpoline_y = set()
        self.retpoline_n = set()
        idx = None
        for i, line in enumerate(content):
            if line.startswith('filename:'):
                if idx is not None:
                    m = ModInfo.from_content(content[idx:i])
                    name = m.module_name
                    self[name] = m
                    self.retpoline_y.add(name) if m.get('retpoline') == 'Y' else None
                    self.retpoline_n.add(name) if m.get('retpoline') == 'N' else None
                idx = i
        if idx is not None and idx < len(content):
            m = ModInfo.from_content(content[idx:])
            name = m.module_name
            self[name] = m
            self.retpoline_y.add(name) if m.get('retpoline') == 'Y' else None
            self.retpoline_n.add(name) if m.get('retpoline') == 'N' else None

        if len(self) == 0:
            raise SkipComponent("No Parsed Contents")


@parser(Specs.modinfo_all)
class ModInfoAll(KernelModulesInfo):
    """
    .. warning::
        This parser is deprecated, please use
        :py:class:`insights.combiners.modinfo.ModulesInfo` instead.

    Class to parse the information about all kernel modules, the module
    info will be stored in dictionary format.

    Sample output::
        filename:       /lib/modules/3.10.0-957.10.1.el7.x86_64/kernel/drivers/net/vmxnet3/vmxnet3.ko.xz
        version:        1.4.14.0-k
        license:        GPL v2
        description:    VMware vmxnet3 virtual NIC driver
        author:         VMware, Inc.
        retpoline:      Y
        rhelversion:    7.6
        srcversion:     7E672688ACACBDD2E363B63
        alias:          pci:v000015ADd000007B0sv*sd*bc*sc*i*
        depends:
        intree:         Y
        vermagic:       3.10.0-957.10.1.el7.x86_64 SMP mod_unload modversions
        signer:         Red Hat Enterprise Linux kernel signing key
        sig_key:        A5:70:18:DF:B6:C9:D6:1F:CF:CE:0A:3D:02:8B:B3:69:BD:76:CA:ED
        sig_hashalgo:   sha256
        filename:       /lib/modules/3.10.0-993.el7.x86_64/kernel/drivers/net/ethernet/intel/i40e/i40e.ko.xz
        firmware:       i40e/i40e-e2-7.13.1.0.fw
        firmware:       i40e/i40e-e1h-7.13.1.0.fw
        version:        2.3.2-k
        license:        GPL
        description:    Intel(R) Ethernet Connection XL710 Network Driver
        author:         Intel Corporation, <e1000-devel@lists.sourceforge.net>
        retpoline:      Y
        rhelversion:    7.7
        srcversion:     DC5C250666ADD8603966656
        alias:          pci:v00008086d0000158Bsv*sd*bc*sc*i*
        alias:          pci:v00008086d0000158Asv*sd*bc*sc*i*
        depends:        ptp
        intree:         Y
        vermagic:       3.10.0-993.el7.x86_64 SMP mod_unload modversions
        signer:         Red Hat Enterprise Linux kernel signing key
        sig_key:        81:7C:CB:07:72:4E:7F:B8:15:24:10:F9:27:2D:AA:CF:80:3E:CE:59
        sig_hashalgo:   sha256
        parm:           debug:Debug level (0=none,...,16=all), Debug mask (0x8XXXXXXX) (uint)
        parm:           int_mode: Force interrupt mode other than MSI-X (1 INT#x; 2 MSI) (int)

    Raises:
        SkipComponent: When nothing need to parse.

    Examples:
        >>> type(modinfo_all)
        <class 'insights.parsers.modinfo.ModInfoAll'>
        >>> 'i40e' in modinfo_all
        True
        >>> modinfo_all['i40e'].module_version
        '2.3.2-k'
        >>> modinfo_all['i40e'].module_path
        '/lib/modules/3.10.0-993.el7.x86_64/kernel/drivers/net/ethernet/intel/i40e/i40e.ko.xz'
        >>> sorted(modinfo_all['i40e'].module_firmware)
        ['i40e/i40e-e1h-7.13.1.0.fw', 'i40e/i40e-e2-7.13.1.0.fw']
        >>> sorted(modinfo_all['i40e'].module_alias)
        ['pci:v00008086d0000158Asv*sd*bc*sc*i*', 'pci:v00008086d0000158Bsv*sd*bc*sc*i*']
        >>> sorted(modinfo_all['i40e'].module_parm)
        ['debug:Debug level (0=none,...,16=all), Debug mask (0x8XXXXXXX) (uint)', 'int_mode: Force interrupt mode other than MSI-X (1 INT#x; 2 MSI) (int)']
        >>> 'vmxnet3' in modinfo_all
        True

    Attributes:
        retpoline_y (set): A set of names of the modules with the attribute "retpoline: Y".
        retpoline_n (set): A set of names of the modules with the attribute "retpoline: N".
    """

    def __init__(self, *args, **kwargs):
        deprecated(
            ModInfoAll,
            "Please use the :class:`insights.combiners.modinfo.ModulesInfo` instead.",
            "3.1.25"
        )
        super(ModInfoAll, self).__init__(*args, **kwargs)


@parser(Specs.modinfo)
class ModInfoEach(CommandParser, ModInfo):
    """
    .. warning::
        This parser is deprecated, please use
        :py:class:`insights.combiners.modinfo.ModulesInfo` instead.

    Parses the output of ``modinfo %s`` command, where %s is any of the loaded modules.

    Sample output::
        filename:       /lib/modules/3.10.0-993.el7.x86_64/kernel/drivers/net/ethernet/intel/i40e/i40e.ko.xz
        firmware:       i40e/i40e-e2-7.13.1.0.fw
        firmware:       i40e/i40e-e1h-7.13.1.0.fw
        version:        2.3.2-k
        license:        GPL
        description:    Intel(R) Ethernet Connection XL710 Network Driver
        author:         Intel Corporation, <e1000-devel@lists.sourceforge.net>
        retpoline:      Y
        rhelversion:    7.7
        srcversion:     DC5C250666ADD8603966656
        alias:          pci:v00008086d0000158Bsv*sd*bc*sc*i*
        alias:          pci:v00008086d0000158Asv*sd*bc*sc*i*
        depends:        ptp
        intree:         Y
        vermagic:       3.10.0-993.el7.x86_64 SMP mod_unload modversions
        signer:         Red Hat Enterprise Linux kernel signing key
        sig_key:        81:7C:CB:07:72:4E:7F:B8:15:24:10:F9:27:2D:AA:CF:80:3E:CE:59
        sig_hashalgo:   sha256
        parm:           debug:Debug level (0=none,...,16=all), Debug mask (0x8XXXXXXX) (uint)
        parm:           int_mode: Force interrupt mode other than MSI-X (1 INT#x; 2 MSI) (int)

    Raises:
        SkipComponent: When nothing is need to parse

    Examples:
        >>> type(modinfo_obj)
        <class 'insights.parsers.modinfo.ModInfoEach'>
        >>> modinfo_obj.module_name
        'i40e'
        >>> modinfo_obj.module_version
        '2.3.2-k'
        >>> modinfo_obj.module_path
        '/lib/modules/3.10.0-993.el7.x86_64/kernel/drivers/net/ethernet/intel/i40e/i40e.ko.xz'
        >>> sorted(modinfo_obj.module_firmware)
        ['i40e/i40e-e1h-7.13.1.0.fw', 'i40e/i40e-e2-7.13.1.0.fw']
        >>> sorted(modinfo_obj.module_alias)
        ['pci:v00008086d0000158Asv*sd*bc*sc*i*', 'pci:v00008086d0000158Bsv*sd*bc*sc*i*']
        >>> sorted(modinfo_obj.module_parm)
        ['debug:Debug level (0=none,...,16=all), Debug mask (0x8XXXXXXX) (uint)', 'int_mode: Force interrupt mode other than MSI-X (1 INT#x; 2 MSI) (int)']
    """

    def __init__(self, *args, **kwargs):
        deprecated(
            ModInfoEach,
            "Please use the :class:`insights.combiners.modinfo.ModulesInfo` instead.",
            "3.1.25"
        )
        super(ModInfoEach, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        self.update(ModInfo.from_content(content))

    @property
    def data(self):
        """
        (dict): This will return the kernel module details when set.
        """
        return self
