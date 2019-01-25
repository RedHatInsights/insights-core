"""
ModInfo_i40e - command ``/sbin/modinfo i40e``
=============================================

The ``/sbin/modinfo i40e`` command provides information about the ``i40e``
kernel module.

Sample ``/sbin/modinfo i40e`` output::

    filename:       /lib/modules/3.10.0-993.el7.x86_64/kernel/drivers/net/ethernet/intel/i40e/i40e.ko.xz
    version:        2.3.2-k
    license:        GPL
    description:    Intel(R) Ethernet Connection XL710 Network Driver
    author:         Intel Corporation, <e1000-devel@lists.sourceforge.net>
    retpoline:      Y
    rhelversion:    7.7
    srcversion:     DC5C250666ADD8603966656
    alias:          pci:v00008086d0000158Bsv*sd*bc*sc*i*
    alias:          pci:v00008086d0000158Asv*sd*bc*sc*i*
    alias:          pci:v00008086d00001588sv*sd*bc*sc*i*
    alias:          pci:v00008086d00001587sv*sd*bc*sc*i*
    alias:          pci:v00008086d000037D3sv*sd*bc*sc*i*
    alias:          pci:v00008086d000037D2sv*sd*bc*sc*i*
    alias:          pci:v00008086d000037D1sv*sd*bc*sc*i*
    alias:          pci:v00008086d000037D0sv*sd*bc*sc*i*
    alias:          pci:v00008086d000037CFsv*sd*bc*sc*i*
    alias:          pci:v00008086d000037CEsv*sd*bc*sc*i*
    alias:          pci:v00008086d00001589sv*sd*bc*sc*i*
    alias:          pci:v00008086d00001586sv*sd*bc*sc*i*
    alias:          pci:v00008086d00001585sv*sd*bc*sc*i*
    alias:          pci:v00008086d00001584sv*sd*bc*sc*i*
    alias:          pci:v00008086d00001583sv*sd*bc*sc*i*
    alias:          pci:v00008086d00001581sv*sd*bc*sc*i*
    alias:          pci:v00008086d00001580sv*sd*bc*sc*i*
    alias:          pci:v00008086d00001574sv*sd*bc*sc*i*
    alias:          pci:v00008086d00001572sv*sd*bc*sc*i*
    depends:        ptp
    intree:         Y
    vermagic:       3.10.0-993.el7.x86_64 SMP mod_unload modversions
    signer:         Red Hat Enterprise Linux kernel signing key
    sig_key:        81:7C:CB:07:72:4E:7F:B8:15:24:10:F9:27:2D:AA:CF:80:3E:CE:59
    sig_hashalgo:   sha256
    parm:           debug:Debug level (0=none,...,16=all), Debug mask (0x8XXXXXXX) (uint)

Examples:

    >>> type(modinfo_obj)
    <class 'insights.parsers.modinfo_i40e.ModInfo_i40e'>
    >>> modinfo_obj.module_name
    'i40e'
    >>> modinfo_obj.module_version
    '2.3.2-k'
    >>> modinfo_obj.module_path
    '/lib/modules/3.10.0-993.el7.x86_64/kernel/drivers/net/ethernet/intel/i40e/i40e.ko.xz'
    >>> 'firmware' in modinfo_obj
    False
"""

from .. import parser, CommandParser
from .. import ModInfo
from insights.specs import Specs


@parser(Specs.modinfo_i40e)
class ModInfo_i40e(CommandParser, ModInfo):
    """Parses output of ``/sbin/modinfo i40e`` command."""
    pass
