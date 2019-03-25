"""
ModInfo - Commands ``/sbin/modinfo <module_name>``
==================================================
Parsers to parse the output of ``/sbin/modinfo <module_name>`` commands.

ModInfoI40e - Command ``/sbin/modinfo i40e``
--------------------------------------------
ModInfoVmxnet3 - Command ``/sbin/modinfo vmxnet3``
--------------------------------------------------
"""

from insights import parser, CommandParser
from insights.parsers import SkipException, ParseException
from insights.specs import Specs


class ModInfo(CommandParser):
    """
    Base class to parse the information about a kernel module, the module
    info will be stored in dictionary format.

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
        SkipException: When content is empty.
        ParseException: When content can not be parsed.

    Examples:
        >>> type(modinfo_obj)
        <class 'insights.parsers.modinfo.ModInfoI40e'>
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

    def parse_content(self, content):
        if (not content) or (not self.file_path):
            raise SkipException("No Contents")

        self.data = {}
        self._module_deps = []
        for line in content:
            line = line.strip()
            if ':' in line:
                key, value = [l.strip() for l in line.split(':', 1)]
                if key not in self.data:
                    self.data[key] = value
                else:
                    old_val = self.data[key]
                    self.data[key] = [old_val] if isinstance(old_val, str) else old_val
                    self.data[key].append(value)

        if not self.data:
            raise ParseException("No Parsed Contents")
        self._module_deps = [mod for mod in self.data.get("depends", '').split(',')]
        self._module_name = self.data.get('filename', '').rsplit("/")[-1].split('.')[0]

    def __contains__(self, option):
        """
        (bool): This will return True if `option` is present kernel info when set, else False
        """
        return option in self.data

    @property
    def module_name(self):
        """
        (str): This will return kernel module name when set, else empty str.
        """
        return self._module_name

    @property
    def module_path(self):
        """
        (str): This will return kernel module path when set, else `None`.
        """
        return self.data.get('filename', '')

    @property
    def module_deps(self):
        """
        (list): This will return the list of kernel modules depend on the kernel
                module when set, else `[]`.
        """
        return self._module_deps

    @property
    def module_firmware(self):
        """
        (list): This will return the list of firmwares used by this module
                when set, else `[]`.
        """
        return self.data.get('firmware', [])

    @property
    def module_alias(self):
        """
        (list): This will return the list of alias to this kernel  module
                when set, else `[]`.
        """
        return self.data.get('alias', [])

    @property
    def module_parm(self):
        """
        (list): This will return the list of parms for this kernel module
                when set, else `[]`.
        """
        return self.data.get('parm', [])

    @property
    def module_version(self):
        """
        (str): This will return the kernel module version when set, else empty string.
        """
        return self.data.get('version', '')

    @property
    def module_signer(self):
        """
        (str): This will return the signer of kernel module when set, else empty string.
        """
        return self.data.get('signer', '')

    def module_details(self):
        """
        (dict): This will return the kernel module details when set.
        """
        return self.data


@parser(Specs.modinfo_i40e)
class ModInfoI40e(ModInfo):
    """
    Parses output of ``/sbin/modinfo i40e`` command.
    Sample ``/sbin/modinfo i40e`` output::

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

    Examples:
        >>> type(modinfo_obj)
        <class 'insights.parsers.modinfo.ModInfoI40e'>
        >>> modinfo_obj.module_name
        'i40e'
        >>> modinfo_obj.module_version
        '2.3.2-k'
        >>> modinfo_obj.module_path
        '/lib/modules/3.10.0-993.el7.x86_64/kernel/drivers/net/ethernet/intel/i40e/i40e.ko.xz'
        >>> 'firmware' in modinfo_obj
        True
        >>> sorted(modinfo_obj.module_firmware) == sorted(['i40e/i40e-e2-7.13.1.0.fw', 'i40e/i40e-e1h-7.13.1.0.fw'])
        True
        >>> sorted(modinfo_obj.module_alias) == sorted(['pci:v00008086d0000158Asv*sd*bc*sc*i*', 'pci:v00008086d0000158Bsv*sd*bc*sc*i*'])
        True
        >>> sorted(modinfo_obj.module_parm) == sorted(['debug:Debug level (0=none,...,16=all), Debug mask (0x8XXXXXXX) (uint)', 'int_mode: Force interrupt mode other than MSI-X (1 INT#x; 2 MSI) (int)'])
        True
    """
    pass


@parser(Specs.modinfo_vmxnet3)
class ModInfoVmxnet3(ModInfo):
    """
    Parses output of ``/sbin/modinfo vmxnet3`` command.
    Sample ``/sbin/modinfo vmxnet3`` output::

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

    Examples:
        >>> type(modinfo_drv)
        <class 'insights.parsers.modinfo.ModInfoVmxnet3'>
        >>> modinfo_drv.module_name
        'vmxnet3'
        >>> modinfo_drv.module_version
        '1.4.14.0-k'
        >>> modinfo_drv.module_signer
        'Red Hat Enterprise Linux kernel signing key'
        >>> modinfo_drv.module_alias
        'pci:v000015ADd000007B0sv*sd*bc*sc*i*'
    """
    pass
