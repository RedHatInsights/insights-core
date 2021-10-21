import doctest
import pytest
from insights.parsers import modinfo, SkipException
from insights.parsers.modinfo import ModInfoI40e, ModInfoVmxnet3, ModInfoIgb, ModInfoIxgbe, ModInfoVeth
from insights.parsers.modinfo import ModInfoEach, ModInfoAll
from insights.tests import context_wrap

MODINFO_I40E = """
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
""".strip()


MODINFO_INTEL = """
filename:       /lib/modules/3.10.0-993.el7.x86_64/kernel/arch/x86/crypto/aesni-intel.ko.xz
alias:          crypto-aes
alias:          aes
license:        GPL
description:    Rijndael (AES) Cipher Algorithm, Intel AES-NI instructions optimized
alias:          crypto-fpu
alias:          fpu
retpoline:      Y
rhelversion:    7.7
srcversion:     975EC794FC6B4D7306E0879
alias:          x86cpu:vendor:*:family:*:model:*:feature:*0099*
depends:        glue_helper,lrw,cryptd,ablk_helper
intree:         Y
vermagic:       3.10.0-993.el7.x86_64 SMP mod_unload modversions
signer:         Red Hat Enterprise Linux kernel signing key
sig_key:        81:7C:CB:07:72:4E:7F:B8:15:24:10:F9:27:2D:AA:CF:80:3E:CE:59
sig_hashalgo:   sha256
""".strip()

MODINFO_BNX2X = """
filename:       /lib/modules/3.10.0-514.el7.x86_64/kernel/drivers/net/ethernet/broadcom/bnx2x/bnx2x.ko
firmware:       bnx2x/bnx2x-e2-7.13.1.0.fw
firmware:       bnx2x/bnx2x-e1h-7.13.1.0.fw
firmware:       bnx2x/bnx2x-e1-7.13.1.0.fw
version:        1.712.30-0
license:        GPL
description:    QLogic BCM57710/57711/57711E/57712/57712_MF/57800/57800_MF/57810/57810_MF/57840/57840_MF Driver
author:         Eliezer Tamir
retpoline:      N
rhelversion:    7.3
srcversion:     E631435423FC99CEF769288
alias:          pci:v000014E4d0000163Fsv*sd*bc*sc*i*
alias:          pci:v000014E4d0000163Esv*sd*bc*sc*i*
alias:          pci:v000014E4d0000163Dsv*sd*bc*sc*i*
alias:          pci:v00001077d000016ADsv*sd*bc*sc*i*
alias:          pci:v000014E4d000016ADsv*sd*bc*sc*i*
alias:          pci:v00001077d000016A4sv*sd*bc*sc*i*
alias:          pci:v000014E4d000016A4sv*sd*bc*sc*i*
alias:          pci:v000014E4d000016ABsv*sd*bc*sc*i*
alias:          pci:v000014E4d000016AFsv*sd*bc*sc*i*
alias:          pci:v000014E4d000016A2sv*sd*bc*sc*i*
alias:          pci:v00001077d000016A1sv*sd*bc*sc*i*
alias:          pci:v000014E4d000016A1sv*sd*bc*sc*i*
alias:          pci:v000014E4d0000168Dsv*sd*bc*sc*i*
alias:          pci:v000014E4d000016AEsv*sd*bc*sc*i*
alias:          pci:v000014E4d0000168Esv*sd*bc*sc*i*
alias:          pci:v000014E4d000016A9sv*sd*bc*sc*i*
alias:          pci:v000014E4d000016A5sv*sd*bc*sc*i*
alias:          pci:v000014E4d0000168Asv*sd*bc*sc*i*
alias:          pci:v000014E4d0000166Fsv*sd*bc*sc*i*
alias:          pci:v000014E4d00001663sv*sd*bc*sc*i*
alias:          pci:v000014E4d00001662sv*sd*bc*sc*i*
alias:          pci:v000014E4d00001650sv*sd*bc*sc*i*
alias:          pci:v000014E4d0000164Fsv*sd*bc*sc*i*
alias:          pci:v000014E4d0000164Esv*sd*bc*sc*i*
depends:        mdio,libcrc32c,ptp
intree:         Y
vermagic:       3.10.0-514.el7.x86_64 SMP mod_unload modversions
signer:         Red Hat Enterprise Linux kernel signing key
sig_key:        75:FE:A1:DF:24:5A:CC:D9:7A:17:FE:3A:36:72:61:E6:5F:8A:1E:60
sig_hashalgo:   sha256
parm:           num_queues: Set number of queues (default is as a number of CPUs) (int)
parm:           disable_tpa: Disable the TPA (LRO) feature (int)
parm:           int_mode: Force interrupt mode other than MSI-X (1 INT#x; 2 MSI) (int)
parm:           dropless_fc: Pause on exhausted host ring (int)
parm:           mrrs: Force Max Read Req Size (0..3) (for debug) (int)
parm:           debug: Default debug msglevel (int)
""".strip()

MODINFO_VMXNET3 = """
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
""".strip()

MODINFO_IGB = """
filename:       /lib/modules/3.10.0-327.10.1.el7.jump7.x86_64/kernel/drivers/net/ethernet/intel/igb/igb.ko
version:        5.2.15-k
license:        GPL
description:    Intel(R) Gigabit Ethernet Network Driver
author:         Intel Corporation, <e1000-devel@lists.sourceforge.net>
rhelversion:    7.2
srcversion:     9CF4D446FA2E882F6BA0A17
alias:          pci:v00008086d000010D6sv*sd*bc*sc*i*
depends:        i2c-core,ptp,dca,i2c-algo-bit
intree:         Y
vermagic:       3.10.0-327.10.1.el7.jump7.x86_64 SMP mod_unload modversions
signer:         Red Hat Enterprise Linux kernel signing key
sig_key:        C9:10:C7:BB:C3:C7:10:A1:68:A6:F3:6D:45:22:90:B7:5A:D4:B0:7A
sig_hashalgo:   sha256
parm:           max_vfs:Maximum number of virtual functions to allocate per physical function (uint)
parm:           debug:Debug level (0=none,...,16=all) (int)
""".strip()

MODINFO_IXGBE = """
filename:       /lib/modules/3.10.0-514.6.1.el7.jump3.x86_64/kernel/drivers/net/ethernet/intel/ixgbe/ixgbe.ko
version:        4.4.0-k-rh7.3
license:        GPL
description:    Intel(R) 10 Gigabit PCI Express Network Driver
author:         Intel Corporation, <linux.nics@intel.com>
rhelversion:    7.3
srcversion:     24F0195E8A357701DE1B32E
alias:          pci:v00008086d000015CEsv*sd*bc*sc*i*
depends:        i2c-core,ptp,dca,i2c-algo-bit
intree:         Y
vermagic:       3.10.0-514.6.1.el7.jump3.x86_64 SMP mod_unload modversions
signer:         Red Hat Enterprise Linux kernel signing key
sig_key:        69:10:6E:D5:83:0D:2C:66:97:41:91:7B:0F:57:D4:1D:95:A2:8A:EB
sig_hashalgo:   sha256
parm:           max_vfs:Maximum number of virtual functions to allocate per physical function (uint)
parm:           debug:Debug level (0=none,...,16=all) (int)
""".strip()

MODINFO_NO = """
""".strip()

MODINFO_NO_1 = """
modinfo ERROR Module i40e not found.
""".strip()

MODINFO_VETH = """
filename:       /lib/modules/3.10.0-327.el7.x86_64/kernel/drivers/net/veth.ko
alias:          rtnl-link-veth
license:        GPL v2
description:    Virtual Ethernet Tunnel
rhelversion:    7.2
srcversion:     25C6BF3D2F35CAF3A252F12
depends:
intree:         Y
vermagic:       3.10.0-327.el7.x86_64 SMP mod_unload modversions
signer:         Red Hat Enterprise Linux kernel signing key
sig_key:        BC:73:C3:CE:E8:9E:5E:AE:99:4A:E5:0A:0D:B1:F0:FE:E3:FC:09:13
sig_hashalgo:   sha256
""".strip()


def test_modinfo():
    modinfo_obj = ModInfoI40e(context_wrap(MODINFO_I40E))
    assert modinfo_obj.module_name == 'i40e'
    assert modinfo_obj.module_version == '2.3.2-k'
    assert modinfo_obj.module_deps == ['ptp']
    assert modinfo_obj.module_signer == 'Red Hat Enterprise Linux kernel signing key'
    assert len(modinfo_obj['alias']) == 2
    assert modinfo_obj['sig_key'] == '81:7C:CB:07:72:4E:7F:B8:15:24:10:F9:27:2D:AA:CF:80:3E:CE:59'
    assert modinfo_obj['vermagic'] == '3.10.0-993.el7.x86_64 SMP mod_unload modversions'
    assert sorted(modinfo_obj['parm']) == sorted(['debug:Debug level (0=none,...,16=all), Debug mask (0x8XXXXXXX) (uint)',
                                                'int_mode: Force interrupt mode other than MSI-X (1 INT#x; 2 MSI) (int)'])
    assert modinfo_obj['description'] == 'Intel(R) Ethernet Connection XL710 Network Driver'
    assert ('signer' in modinfo_obj) is True
    assert modinfo_obj.module_path == "/lib/modules/3.10.0-993.el7.x86_64/kernel/drivers/net/ethernet/intel/i40e/i40e.ko.xz"

    modinfo_obj = ModInfoI40e(context_wrap(MODINFO_INTEL))
    assert len(modinfo_obj['alias']) == 5
    assert sorted(modinfo_obj['alias']) == sorted(['aes', 'crypto-aes', 'crypto-fpu', 'fpu', 'x86cpu:vendor:*:family:*:model:*:feature:*0099*'])
    assert ('parm' in modinfo_obj) is False
    assert modinfo_obj.module_name == 'aesni-intel'
    assert modinfo_obj['description'] == 'Rijndael (AES) Cipher Algorithm, Intel AES-NI instructions optimized'
    assert modinfo_obj['rhelversion'] == '7.7'
    assert modinfo_obj.module_signer == 'Red Hat Enterprise Linux kernel signing key'
    assert modinfo_obj.module_deps == ['glue_helper', 'lrw', 'cryptd', 'ablk_helper']
    assert modinfo_obj['sig_key'] == '81:7C:CB:07:72:4E:7F:B8:15:24:10:F9:27:2D:AA:CF:80:3E:CE:59'

    modinfo_obj = ModInfoI40e(context_wrap(MODINFO_BNX2X))
    assert len(modinfo_obj['alias']) == 24
    assert len(modinfo_obj['parm']) == 6
    assert len(modinfo_obj['firmware']) == 3
    assert sorted(modinfo_obj['firmware']) == sorted(['bnx2x/bnx2x-e2-7.13.1.0.fw', 'bnx2x/bnx2x-e1h-7.13.1.0.fw', 'bnx2x/bnx2x-e1-7.13.1.0.fw'])
    assert modinfo_obj.module_name == 'bnx2x'
    assert modinfo_obj.module_path == '/lib/modules/3.10.0-514.el7.x86_64/kernel/drivers/net/ethernet/broadcom/bnx2x/bnx2x.ko'
    assert modinfo_obj.module_signer == 'Red Hat Enterprise Linux kernel signing key'
    assert sorted(modinfo_obj.module_deps) == sorted(['mdio', 'libcrc32c', 'ptp'])

    modinfo_igb = ModInfoIgb(context_wrap(MODINFO_IGB))
    assert modinfo_igb.get('alias') == 'pci:v00008086d000010D6sv*sd*bc*sc*i*'
    assert modinfo_igb.module_name == 'igb'
    assert modinfo_igb.module_path == '/lib/modules/3.10.0-327.10.1.el7.jump7.x86_64/kernel/drivers/net/ethernet/intel/igb/igb.ko'

    modinfo_ixgbe = ModInfoIxgbe(context_wrap(MODINFO_IXGBE))
    assert modinfo_ixgbe.get('alias') == 'pci:v00008086d000015CEsv*sd*bc*sc*i*'
    assert modinfo_ixgbe.module_name == 'ixgbe'
    assert modinfo_ixgbe.module_path == '/lib/modules/3.10.0-514.6.1.el7.jump3.x86_64/kernel/drivers/net/ethernet/intel/ixgbe/ixgbe.ko'

    modinfo_drv = ModInfoVmxnet3(context_wrap(MODINFO_VMXNET3))
    assert modinfo_drv.get('alias') == 'pci:v000015ADd000007B0sv*sd*bc*sc*i*'
    assert len(modinfo_drv.module_parm) == 0
    assert len(modinfo_drv.module_firmware) == 0
    assert modinfo_drv.module_name == 'vmxnet3'
    assert modinfo_drv.module_path == '/lib/modules/3.10.0-957.10.1.el7.x86_64/kernel/drivers/net/vmxnet3/vmxnet3.ko.xz'

    assert sorted(modinfo_obj['firmware']) == sorted(['bnx2x/bnx2x-e2-7.13.1.0.fw', 'bnx2x/bnx2x-e1h-7.13.1.0.fw', 'bnx2x/bnx2x-e1-7.13.1.0.fw'])

    modinfo_drv = ModInfoVeth(context_wrap(MODINFO_VETH))
    assert modinfo_drv.module_name == 'veth'
    assert modinfo_drv.module_path == '/lib/modules/3.10.0-327.el7.x86_64/kernel/drivers/net/veth.ko'
    assert modinfo_drv.module_signer == 'Red Hat Enterprise Linux kernel signing key'

    with pytest.raises(SkipException) as exc:
        modinfo_obj = ModInfoI40e(context_wrap(MODINFO_NO))
    assert 'No Contents' in str(exc)

    with pytest.raises(SkipException) as exc:
        modinfo_obj = ModInfoI40e(context_wrap(MODINFO_NO_1))
    assert 'No Parsed Contents' in str(exc)

    with pytest.raises(SkipException) as exc:
        modinfo_drv = ModInfoVmxnet3(context_wrap(MODINFO_NO))
    assert 'No Contents' in str(exc)

    with pytest.raises(SkipException) as exc:
        modinfo_drv = ModInfoVmxnet3(context_wrap(MODINFO_NO_1))
    assert 'No Parsed Contents' in str(exc)

    with pytest.raises(SkipException) as exc:
        modinfo_drv = ModInfoVeth(context_wrap(MODINFO_NO))
    assert 'No Contents' in str(exc)

    with pytest.raises(SkipException) as exc:
        modinfo_drv = ModInfoVeth(context_wrap(MODINFO_NO_1))
    assert 'No Parsed Contents' in str(exc)


def test_modinfoeach():
    modinfo_obj = ModInfoEach(context_wrap(MODINFO_I40E))
    assert modinfo_obj.module_name == 'i40e'
    assert modinfo_obj.module_version == '2.3.2-k'
    assert modinfo_obj.module_deps == ['ptp']
    assert modinfo_obj.module_signer == 'Red Hat Enterprise Linux kernel signing key'
    assert len(modinfo_obj['alias']) == 2
    assert modinfo_obj.module_details['sig_key'] == '81:7C:CB:07:72:4E:7F:B8:15:24:10:F9:27:2D:AA:CF:80:3E:CE:59'
    assert modinfo_obj['vermagic'] == '3.10.0-993.el7.x86_64 SMP mod_unload modversions'
    assert sorted(modinfo_obj['parm']) == sorted(['debug:Debug level (0=none,...,16=all), Debug mask (0x8XXXXXXX) (uint)',
                                                       'int_mode: Force interrupt mode other than MSI-X (1 INT#x; 2 MSI) (int)'])
    assert modinfo_obj['description'] == 'Intel(R) Ethernet Connection XL710 Network Driver'
    assert ('signer' in modinfo_obj) is True
    assert modinfo_obj.module_path == "/lib/modules/3.10.0-993.el7.x86_64/kernel/drivers/net/ethernet/intel/i40e/i40e.ko.xz"


def test_modinfoall():
    context = context_wrap(
            '{0}\n{1}\n{2}\n{3}\n{4}\n'.format(
                MODINFO_I40E,
                MODINFO_VMXNET3,
                MODINFO_IGB,
                MODINFO_VETH,
                MODINFO_IXGBE)
    )
    modinfo_all = ModInfoAll(context)
    assert sorted(modinfo_all.keys()) == sorted(['i40e', 'vmxnet3', 'igb', 'veth', 'ixgbe'])
    assert modinfo_all['i40e'].module_version == '2.3.2-k'
    assert modinfo_all['i40e'].module_deps == ['ptp']
    assert modinfo_all['i40e'].module_signer == 'Red Hat Enterprise Linux kernel signing key'
    assert len(modinfo_all['i40e']['alias']) == 2
    assert modinfo_all['i40e'].module_details['sig_key'] == '81:7C:CB:07:72:4E:7F:B8:15:24:10:F9:27:2D:AA:CF:80:3E:CE:59'
    assert modinfo_all['i40e']['vermagic'] == '3.10.0-993.el7.x86_64 SMP mod_unload modversions'
    assert sorted(modinfo_all['i40e']['parm']) == sorted(['debug:Debug level (0=none,...,16=all), Debug mask (0x8XXXXXXX) (uint)',
                                                       'int_mode: Force interrupt mode other than MSI-X (1 INT#x; 2 MSI) (int)'])
    assert modinfo_all['i40e']['description'] == 'Intel(R) Ethernet Connection XL710 Network Driver'
    assert ('signer' in modinfo_all['i40e']) is True
    assert modinfo_all['i40e'].module_path == "/lib/modules/3.10.0-993.el7.x86_64/kernel/drivers/net/ethernet/intel/i40e/i40e.ko.xz"

    assert modinfo_all['igb'].get('alias') == 'pci:v00008086d000010D6sv*sd*bc*sc*i*'
    assert modinfo_all['igb'].module_name == 'igb'
    assert modinfo_all['igb'].module_path == '/lib/modules/3.10.0-327.10.1.el7.jump7.x86_64/kernel/drivers/net/ethernet/intel/igb/igb.ko'

    with pytest.raises(SkipException) as exc:
        ModInfoAll(context_wrap(MODINFO_NO_1))
    assert 'No Parsed Contents' in str(exc)

    with pytest.raises(SkipException) as exc:
        ModInfoAll(context_wrap(''))
    assert 'No Contents' in str(exc)


def test_modinfo_doc_examples():
    env = {
            'modinfo_obj': ModInfoEach(context_wrap(MODINFO_I40E)),
            'modinfo_i40e': ModInfoI40e(context_wrap(MODINFO_I40E)),
            'modinfo_drv': ModInfoVmxnet3(context_wrap(MODINFO_VMXNET3)),
            'modinfo_igb': ModInfoIgb(context_wrap(MODINFO_IGB)),
            'modinfo_veth': ModInfoVeth(context_wrap(MODINFO_VETH)),
            'modinfo_ixgbe': ModInfoIxgbe(context_wrap(MODINFO_IXGBE)),
            'modinfo_all': ModInfoAll(context_wrap("{0}\n{1}".format(MODINFO_VMXNET3, MODINFO_I40E)))
    }
    failed, total = doctest.testmod(modinfo, globs=env)
    assert failed == 0
