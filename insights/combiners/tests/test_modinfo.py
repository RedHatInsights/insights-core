from insights.parsers.modinfo import ModInfoEach, ModInfoAll
from insights.combiners.modinfo import ModInfo
from insights.parsers.tests.test_modinfo import (
        MODINFO_I40E, MODINFO_INTEL,
        MODINFO_BNX2X, MODINFO_IGB, MODINFO_IXGBE,
        MODINFO_VMXNET3, MODINFO_VETH)
from insights.tests import context_wrap
import doctest
from insights.combiners import modinfo
from insights.core.dr import SkipComponent
import pytest


def test_modinfo_each():

    with pytest.raises(SkipComponent):
        ModInfo({}, [])

    modinfo_i40e = ModInfoEach(context_wrap(MODINFO_I40E))
    modinfo_intel = ModInfoEach(context_wrap(MODINFO_INTEL))
    modinfo_bnx2x = ModInfoEach(context_wrap(MODINFO_BNX2X))
    modinfo_igb = ModInfoEach(context_wrap(MODINFO_IGB))
    modinfo_ixgbe = ModInfoEach(context_wrap(MODINFO_IXGBE))
    modinfo_vmxnet3 = ModInfoEach(context_wrap(MODINFO_VMXNET3))
    modinfo_veth = ModInfoEach(context_wrap(MODINFO_VETH))
    comb = ModInfo(
            None, [
                modinfo_i40e,
                modinfo_intel,
                modinfo_bnx2x,
                modinfo_igb,
                modinfo_ixgbe,
                modinfo_vmxnet3,
                modinfo_veth,
            ]
    )
    assert sorted(comb.retpoline_y) == sorted(['aesni-intel', 'i40e', 'vmxnet3'])
    assert sorted(comb.retpoline_n) == sorted(['bnx2x'])
    assert sorted(comb.keys()) == sorted(['i40e', 'aesni-intel', 'bnx2x', 'vmxnet3', 'igb', 'ixgbe', 'veth'])

    modinfo_obj = comb['i40e']
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

    modinfo_obj = comb['aesni-intel']
    assert len(modinfo_obj['alias']) == 5
    assert sorted(modinfo_obj['alias']) == sorted(['aes', 'crypto-aes', 'crypto-fpu', 'fpu', 'x86cpu:vendor:*:family:*:model:*:feature:*0099*'])
    assert ('parm' in modinfo_obj) is False
    assert modinfo_obj.module_name == 'aesni-intel'
    assert modinfo_obj['description'] == 'Rijndael (AES) Cipher Algorithm, Intel AES-NI instructions optimized'
    assert modinfo_obj['rhelversion'] == '7.7'
    assert modinfo_obj.module_signer == 'Red Hat Enterprise Linux kernel signing key'
    assert modinfo_obj.module_deps == ['glue_helper', 'lrw', 'cryptd', 'ablk_helper']
    assert modinfo_obj['sig_key'] == '81:7C:CB:07:72:4E:7F:B8:15:24:10:F9:27:2D:AA:CF:80:3E:CE:59'

    modinfo_obj = comb['bnx2x']
    assert len(modinfo_obj['alias']) == 24
    assert len(modinfo_obj['parm']) == 6
    assert len(modinfo_obj['firmware']) == 3
    assert sorted(modinfo_obj['firmware']) == sorted(['bnx2x/bnx2x-e2-7.13.1.0.fw', 'bnx2x/bnx2x-e1h-7.13.1.0.fw', 'bnx2x/bnx2x-e1-7.13.1.0.fw'])
    assert modinfo_obj.module_name == 'bnx2x'
    assert modinfo_obj.module_path == '/lib/modules/3.10.0-514.el7.x86_64/kernel/drivers/net/ethernet/broadcom/bnx2x/bnx2x.ko'
    assert modinfo_obj.module_signer == 'Red Hat Enterprise Linux kernel signing key'
    assert sorted(modinfo_obj.module_deps) == sorted(['mdio', 'libcrc32c', 'ptp'])

    modinfo_obj = comb['igb']
    assert modinfo_igb.get('alias') == 'pci:v00008086d000010D6sv*sd*bc*sc*i*'
    assert modinfo_igb.module_name == 'igb'
    assert modinfo_igb.module_path == '/lib/modules/3.10.0-327.10.1.el7.jump7.x86_64/kernel/drivers/net/ethernet/intel/igb/igb.ko'

    modinfo_obj = comb['ixgbe']
    assert modinfo_ixgbe.get('alias') == 'pci:v00008086d000015CEsv*sd*bc*sc*i*'
    assert modinfo_ixgbe.module_name == 'ixgbe'
    assert modinfo_ixgbe.module_path == '/lib/modules/3.10.0-514.6.1.el7.jump3.x86_64/kernel/drivers/net/ethernet/intel/ixgbe/ixgbe.ko'

    modinfo_drv = comb['vmxnet3']
    assert modinfo_drv.get('alias') == 'pci:v000015ADd000007B0sv*sd*bc*sc*i*'
    assert len(modinfo_drv.module_parm) == 0
    assert len(modinfo_drv.module_firmware) == 0
    assert modinfo_drv.module_name == 'vmxnet3'
    assert modinfo_drv.module_path == '/lib/modules/3.10.0-957.10.1.el7.x86_64/kernel/drivers/net/vmxnet3/vmxnet3.ko.xz'

    modinfo_drv = comb['veth']
    assert modinfo_drv.module_name == 'veth'
    assert modinfo_drv.module_path == '/lib/modules/3.10.0-327.el7.x86_64/kernel/drivers/net/veth.ko'
    assert modinfo_drv.module_signer == 'Red Hat Enterprise Linux kernel signing key'


def test_modinfo_all():

    with pytest.raises(SkipComponent):
        ModInfo({}, [])

    context = context_wrap(
            '{0}\n{1}\n{2}\n{3}\n{4}\n{5}'.format(
                MODINFO_I40E,
                MODINFO_INTEL,
                MODINFO_BNX2X,
                MODINFO_IGB,
                MODINFO_IXGBE,
                MODINFO_VMXNET3,
                # MODINFO_VETH <- Remove from ModInfAll
            )
    )

    modinfo_i40e = ModInfoEach(context_wrap(MODINFO_I40E))
    modinfo_intel = ModInfoEach(context_wrap(MODINFO_INTEL))
    modinfo_bnx2x = ModInfoEach(context_wrap(MODINFO_BNX2X))
    modinfo_igb = ModInfoEach(context_wrap(MODINFO_IGB))
    modinfo_ixgbe = ModInfoEach(context_wrap(MODINFO_IXGBE))
    modinfo_vmxnet3 = ModInfoEach(context_wrap(MODINFO_VMXNET3))
    modinfo_veth = ModInfoEach(context_wrap(MODINFO_VETH))
    comb = ModInfo(
            ModInfoAll(context),
            [
                modinfo_i40e,
                modinfo_intel,
                modinfo_bnx2x,
                modinfo_igb,
                modinfo_ixgbe,
                modinfo_vmxnet3,
                modinfo_veth,  # <- But leave in ModInfoEach
            ]
    )

    assert 'veth' not in comb  # Check it here: not found

    assert sorted(comb.retpoline_y) == sorted(['aesni-intel', 'i40e', 'vmxnet3'])
    assert sorted(comb.retpoline_n) == sorted(['bnx2x'])
    assert sorted(comb.keys()) == sorted(['i40e', 'aesni-intel', 'bnx2x', 'vmxnet3', 'igb', 'ixgbe'])

    modinfo_obj = comb['i40e']
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

    modinfo_obj = comb['aesni-intel']
    assert len(modinfo_obj['alias']) == 5
    assert sorted(modinfo_obj['alias']) == sorted(['aes', 'crypto-aes', 'crypto-fpu', 'fpu', 'x86cpu:vendor:*:family:*:model:*:feature:*0099*'])
    assert ('parm' in modinfo_obj) is False
    assert modinfo_obj.module_name == 'aesni-intel'
    assert modinfo_obj['description'] == 'Rijndael (AES) Cipher Algorithm, Intel AES-NI instructions optimized'
    assert modinfo_obj['rhelversion'] == '7.7'
    assert modinfo_obj.module_signer == 'Red Hat Enterprise Linux kernel signing key'
    assert modinfo_obj.module_deps == ['glue_helper', 'lrw', 'cryptd', 'ablk_helper']
    assert modinfo_obj['sig_key'] == '81:7C:CB:07:72:4E:7F:B8:15:24:10:F9:27:2D:AA:CF:80:3E:CE:59'

    modinfo_obj = comb['bnx2x']
    assert len(modinfo_obj['alias']) == 24
    assert len(modinfo_obj['parm']) == 6
    assert len(modinfo_obj['firmware']) == 3
    assert sorted(modinfo_obj['firmware']) == sorted(['bnx2x/bnx2x-e2-7.13.1.0.fw', 'bnx2x/bnx2x-e1h-7.13.1.0.fw', 'bnx2x/bnx2x-e1-7.13.1.0.fw'])
    assert modinfo_obj.module_name == 'bnx2x'
    assert modinfo_obj.module_path == '/lib/modules/3.10.0-514.el7.x86_64/kernel/drivers/net/ethernet/broadcom/bnx2x/bnx2x.ko'
    assert modinfo_obj.module_signer == 'Red Hat Enterprise Linux kernel signing key'
    assert sorted(modinfo_obj.module_deps) == sorted(['mdio', 'libcrc32c', 'ptp'])

    modinfo_obj = comb['igb']
    assert modinfo_igb.get('alias') == 'pci:v00008086d000010D6sv*sd*bc*sc*i*'
    assert modinfo_igb.module_name == 'igb'
    assert modinfo_igb.module_path == '/lib/modules/3.10.0-327.10.1.el7.jump7.x86_64/kernel/drivers/net/ethernet/intel/igb/igb.ko'

    modinfo_obj = comb['ixgbe']
    assert modinfo_ixgbe.get('alias') == 'pci:v00008086d000015CEsv*sd*bc*sc*i*'
    assert modinfo_ixgbe.module_name == 'ixgbe'
    assert modinfo_ixgbe.module_path == '/lib/modules/3.10.0-514.6.1.el7.jump3.x86_64/kernel/drivers/net/ethernet/intel/ixgbe/ixgbe.ko'

    modinfo_drv = comb['vmxnet3']
    assert modinfo_drv.get('alias') == 'pci:v000015ADd000007B0sv*sd*bc*sc*i*'
    assert len(modinfo_drv.module_parm) == 0
    assert len(modinfo_drv.module_firmware) == 0
    assert modinfo_drv.module_name == 'vmxnet3'
    assert modinfo_drv.module_path == '/lib/modules/3.10.0-957.10.1.el7.x86_64/kernel/drivers/net/vmxnet3/vmxnet3.ko.xz'


def test_modinfo_doc_examples():
    modinfo_i40e = ModInfoEach(context_wrap(MODINFO_I40E))
    modinfo_intel = ModInfoEach(context_wrap(MODINFO_INTEL))
    modinfo_bnx2x = ModInfoEach(context_wrap(MODINFO_BNX2X))
    modinfo_igb = ModInfoEach(context_wrap(MODINFO_IGB))
    modinfo_ixgbe = ModInfoEach(context_wrap(MODINFO_IXGBE))
    modinfo_vmxnet3 = ModInfoEach(context_wrap(MODINFO_VMXNET3))
    modinfo_veth = ModInfoEach(context_wrap(MODINFO_VETH))
    comb = ModInfo(
            None, [
                modinfo_i40e,
                modinfo_intel,
                modinfo_bnx2x,
                modinfo_igb,
                modinfo_ixgbe,
                modinfo_vmxnet3,
                modinfo_veth]
    )
    env = {'modinfo_obj': comb}
    failed, total = doctest.testmod(modinfo, globs=env)
    assert failed == 0
