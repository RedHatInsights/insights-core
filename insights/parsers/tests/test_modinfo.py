import doctest
import pytest
from insights.parsers import modinfo, ParseException, SkipException
from insights.parsers.modinfo import ModInfoI40e, ModInfoVmxnet3
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

MODINFO_NO = """
""".strip()

MODINFO_NO_1 = """
modinfo ERROR Module i40e not found.
""".strip()


def test_modinfo():
    modinfo_obj = ModInfoI40e(context_wrap(MODINFO_I40E))
    assert modinfo_obj.module_name == 'i40e'
    assert modinfo_obj.module_version == '2.3.2-k'
    assert modinfo_obj.module_deps == ['ptp']
    assert modinfo_obj.module_signer == 'Red Hat Enterprise Linux kernel signing key'
    assert len(modinfo_obj.data['alias']) == 2
    assert modinfo_obj.data['sig_key'] == '81:7C:CB:07:72:4E:7F:B8:15:24:10:F9:27:2D:AA:CF:80:3E:CE:59'
    assert modinfo_obj.data['vermagic'] == '3.10.0-993.el7.x86_64 SMP mod_unload modversions'
    assert sorted(modinfo_obj.data['parm']) == sorted(['debug:Debug level (0=none,...,16=all), Debug mask (0x8XXXXXXX) (uint)',
                                                'int_mode: Force interrupt mode other than MSI-X (1 INT#x; 2 MSI) (int)'])
    assert modinfo_obj.data['description'] == 'Intel(R) Ethernet Connection XL710 Network Driver'
    assert ('signer' in modinfo_obj) is True
    assert modinfo_obj.module_path == "/lib/modules/3.10.0-993.el7.x86_64/kernel/drivers/net/ethernet/intel/i40e/i40e.ko.xz"

    modinfo_obj = ModInfoI40e(context_wrap(MODINFO_INTEL))
    assert len(modinfo_obj.data['alias']) == 5
    assert sorted(modinfo_obj.data['alias']) == sorted(['aes', 'crypto-aes', 'crypto-fpu', 'fpu', 'x86cpu:vendor:*:family:*:model:*:feature:*0099*'])
    assert ('parm' in modinfo_obj) is False
    assert modinfo_obj.module_name == 'aesni-intel'
    assert modinfo_obj.data['description'] == 'Rijndael (AES) Cipher Algorithm, Intel AES-NI instructions optimized'
    assert modinfo_obj.data['rhelversion'] == '7.7'
    assert modinfo_obj.module_signer == 'Red Hat Enterprise Linux kernel signing key'
    assert modinfo_obj.module_deps == ['glue_helper', 'lrw', 'cryptd', 'ablk_helper']
    assert modinfo_obj.data['sig_key'] == '81:7C:CB:07:72:4E:7F:B8:15:24:10:F9:27:2D:AA:CF:80:3E:CE:59'

    modinfo_obj = ModInfoI40e(context_wrap(MODINFO_BNX2X))
    assert len(modinfo_obj.data['alias']) == 24
    assert len(modinfo_obj.data['parm']) == 6
    assert len(modinfo_obj.data['firmware']) == 3
    assert sorted(modinfo_obj.data['firmware']) == sorted(['bnx2x/bnx2x-e2-7.13.1.0.fw', 'bnx2x/bnx2x-e1h-7.13.1.0.fw', 'bnx2x/bnx2x-e1-7.13.1.0.fw'])
    assert modinfo_obj.module_name == 'bnx2x'
    assert modinfo_obj.module_path == '/lib/modules/3.10.0-514.el7.x86_64/kernel/drivers/net/ethernet/broadcom/bnx2x/bnx2x.ko'
    assert modinfo_obj.module_signer == 'Red Hat Enterprise Linux kernel signing key'
    assert sorted(modinfo_obj.module_deps) == sorted(['mdio', 'libcrc32c', 'ptp'])

    modinfo_drv = ModInfoVmxnet3(context_wrap(MODINFO_VMXNET3))
    assert modinfo_drv.data.get('alias') == 'pci:v000015ADd000007B0sv*sd*bc*sc*i*'
    assert len(modinfo_drv.module_parm) == 0
    assert len(modinfo_drv.module_firmware) == 0
    assert modinfo_drv.module_name == 'vmxnet3'
    assert modinfo_drv.module_path == '/lib/modules/3.10.0-957.10.1.el7.x86_64/kernel/drivers/net/vmxnet3/vmxnet3.ko.xz'

    assert sorted(modinfo_obj.data['firmware']) == sorted(['bnx2x/bnx2x-e2-7.13.1.0.fw', 'bnx2x/bnx2x-e1h-7.13.1.0.fw', 'bnx2x/bnx2x-e1-7.13.1.0.fw'])

    with pytest.raises(SkipException) as exc:
        modinfo_obj = ModInfoI40e(context_wrap(MODINFO_NO))
    assert 'No Contents' in str(exc)

    with pytest.raises(ParseException) as exc:
        modinfo_obj = ModInfoI40e(context_wrap(MODINFO_NO_1))
    assert 'No Parsed Contents' in str(exc)

    with pytest.raises(SkipException) as exc:
        modinfo_drv = ModInfoVmxnet3(context_wrap(MODINFO_NO))
    assert 'No Contents' in str(exc)

    with pytest.raises(ParseException) as exc:
        modinfo_drv = ModInfoVmxnet3(context_wrap(MODINFO_NO_1))
    assert 'No Parsed Contents' in str(exc)


def test_modinfo_doc_examples():
    env = {'modinfo_obj': ModInfoI40e(context_wrap(MODINFO_I40E)),
           'modinfo_drv': ModInfoVmxnet3(context_wrap(MODINFO_VMXNET3))}
    failed, total = doctest.testmod(modinfo, globs=env)
    assert failed == 0
