"""
ModInfoI40e - command ``/sbin/modinfo i40e``
=============================================

The ``/sbin/modinfo i40e`` command provides information about the ``i40e``
kernel module.

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

from .. import parser
from .. import ModInfo
from insights.specs import Specs


@parser(Specs.modinfo_i40e)
class ModInfoI40e(ModInfo):
    """Parses output of ``/sbin/modinfo i40e`` command."""
    pass
