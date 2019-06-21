from insights.tests import context_wrap
from insights.parsers.grub_conf import Grub1Config, Grub2Config, Grub1EFIConfig
from insights.parsers.grub_conf import Grub2Grubenv
import pytest

# RHEL7
GRUB2_CFG_1 = """
if [ -s $prefix/grubenv ]; then
  load_env
fi
#[...]
if [ x"${feature_menuentry_id}" = xy ]; then
  menuentry_id_option="--id"
else
  menuentry_id_option=""
fi
## BEGIN /etc/grub.d/10_linux ###
menuentry 'Red Hat Enterprise Linux Server, with Linux 3.10.0-123.9.3.el7.x86_64' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-123.9.3.el7.x86_64-advanced-5a1c841f-5cfe-4d59-b3a0-4b788369d6cb'
   {load_video
    set gfxpayload=keep
    insmod part_msdos
    set root='hd0,msdos1'
    if [ x$feature_platform_search_hint = xy ]; then
      search --no-floppy --fs-uuid --set=root --hint-bios=hd0,msdos1 --hint-efi=hd0,msdos1 --hint-baremetal=ahci0,msdos1 --hint='hd0,msdos1'  93f2c0dc-6201-4d26-a610-4b3998983ea2
      if [ -s $prefix/grubenv ]; then
        load_env
      fi
    else
      search --no-floppy --fs-uuid --set=root 93f2c0dc-6201-4d26-a610-4b3998983ea2
    fi
    linux16 /vmlinuz-3.10.0-123.9.3.el7.x86_64 root=UUID=5a1c841f-5cfe-4d59-b3a0-4b788369d6cb ro crashkernel=auto  vconsole.font=latarcyrheb-sun16 console=ttyS0,38400 rd.lvm.lv=VG_RACS-CCP/lv-rootfs vconsole.keymap=us LANG=en_US.UTF-8
    initrd16 /initramfs-3.10.0-123.9.3.el7.x86_64.img
    insmod gzio}
menuentry 'Red Hat Enterprise Linux Server, with Linux 0-rescue-00c2fbfaa85544e48d6ca1d919fa2dd3' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-0-rescue-00c2fbfaa85544e48d6ca1d919fa2dd3-advanced-5a1c841f-5cfe-4d59-b3a0-4b788369d6cb'
    {
    insmod part_msdos
    insmod ext2
    set root='hd0,msdos1'
    if [ x$feature_platform_search_hint = xy ]; then
      search --no-floppy --fs-uuid --set=root --hint-bios=hd0,msdos1 --hint-efi=hd0,msdos1 --hint-baremetal=ahci0,msdos1 --hint='hd0,msdos1'  93f2c0dc-6201-4d26-a610-4b3998983ea2
    else
      search --no-floppy --fs-uuid --set=root 93f2c0dc-6201-4d26-a610-4b3998983ea2
    fi
    linux16 /vmlinuz-0-rescue-00c2fbfaa85544e48d6ca1d919fa2dd3 root=UUID=5a1c841f-5cfe-4d59-b3a0-4b788369d6cb ro crashkernel=auto  vconsole.font=latarcyrheb-sun16 console=ttyS0,38400 rd.lvm.lv=VG_RACS-CCP/lv-rootfs vconsole.keymap=us
    initrd16 /initramfs-0-rescue-00c2fbfaa85544e48d6ca1d919fa2dd3.img
}
""".strip()

# RHEL7
GRUB2_CFG_2 = """
### BEGIN /etc/grub.d/10_linux ###
menuentry 'Red Hat Enterprise Linux Server (3.10.0-229.el7.x86_64) 7.0 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-123.el7.x86_64-advanced-7f18fec3-a016-42ab-9bb9-6e7f6a5985ca' {
    linux16 /vmlinuz-3.10.0-229.el7.x86_64 root=/dev/mapper/rhel-root ro rd.lvm.lv=rhel/root crashkernel=auto  rd.lvm.lv=rhel/swap vconsole.font=latarcyrheb-sun16 vconsole.keymap=us rhgb quiet LANG=en_AU.UTF-8
    initrd16 /initramfs-3.10.0-229.el7.x86_64.img
}
menuentry 'Red Hat Enterprise Linux Server (3.10.0-123.13.2.el7.x86_64) 7.0 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-123.el7.x86_64-advanced-7f18fec3-a016-42ab-9bb9-6e7f6a5985ca' {
    linux16 /vmlinuz-3.10.0-123.13.2.el7.x86_64 root=/dev/mapper/rhel-root ro rd.lvm.lv=rhel/root crashkernel=auto  rd.lvm.lv=rhel/swap vconsole.font=latarcyrheb-sun16 vconsole.keymap=us rhgb quiet LANG=en_AU.UTF-8
    initrd16 /initramfs-3.10.0-123.13.2.el7.x86_64.img
}
menuentry 'Red Hat Enterprise Linux Server, with Linux 3.10.0-123.el7.x86_64' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-123.el7.x86_64-advanced-7f18fec3-a016-42ab-9bb9-6e7f6a5985ca' {
    linux16 /vmlinuz-3.10.0-123.el7.x86_64 root=UUID=7f18fec3-a016-42ab-9bb9-6e7f6a5985ca ro rd.lvm.lv=rhel/root crashkernel=auto  rd.lvm.lv=rhel/swap vconsole.font=latarcyrheb-sun16 vconsole.keymap=us rhgb quiet LANG=en_AU.UTF-8
    initrd16 /initramfs-3.10.0-123.el7.x86_64.img
}
menuentry 'Red Hat Enterprise Linux Server, with Linux 0-rescue-13798ffcbc1ed4374f3f2e0fa6c923ad' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-0-rescue-13798ffcbc1ed4374f3f2e0fa6c923ad-advanced-7f18fec3-a016-42ab-9bb9-6e7f6a5985ca' {
    linux16 /vmlinuz-0-rescue-13798ffcbc1ed4374f3f2e0fa6c923ad root=UUID=7f18fec3-a016-42ab-9bb9-6e7f6a5985ca ro rd.lvm.lv=rhel/root crashkernel=auto  rd.lvm.lv=rhel/swap vconsole.font=latarcyrheb-sun16 vconsole.keymap=us rhgb quiet
    initrd16 /initramfs-0-rescue-13798ffcbc1ed4374f3f2e0fa6c923ad.img
}
""".strip()

# RHEL5/6
GRUB1_CONF_3 = """
# grub.conf generated by anaconda
#
# Note that you do not have to rerun grub after making changes to this file
# NOTICE:  You have a /boot partition.  This means that
#          all kernel and initrd paths are relative to /boot/, eg.
#          root (hd0,0)
#          kernel /vmlinuz-version ro root=/dev/cciss/c0d0p3
#          initrd /initrd-version.img
#boot=/dev/cciss/c0d0
default=1
# fallback=0 # commented out by Proliant HBA install script
timeout=5
splashimage=(hd0,0)/grub/splash.xpm.gz
hiddenmenu
title Red Hat Enterprise Linux Server (2.6.18-194.8.1.el5)
    root (hd0,0)
    kernel /vmlinuz-2.6.18-194.8.1.el5 ro root=LABEL=/1 crashkernel=128M@16M
    initrd /initrd-2.6.18-194.8.1.el5.img

title Red Hat Enterprise Linux Server (2.6.18-194.17.1.el5)
    root (hd0,0)
    kernel /vmlinuz-2.6.18-194.17.1.el5 ro root=LABEL=/1 crashkernel=128M@16M
    module /initramfs-2.6.18-194.8.1.el5.img
""".strip()

# Incorrect `initrd` and `default`
GRUB1_CONF_4 = """
default=a
title (2.6.18-194.8.1.el5)
    kernel /vmlinuz-2.6.18-194.8.1.el5 ro root=LABEL=/1 crashkernel=128M@16M
    module /2.6.18-194.8.1.el5.img
""".strip()

# Empty kernel
GRUB1_CONF_5 = """
defaults=0
title (2.6.18-194.8.1.el5)
    kernel
    module /2.6.18-194.8.1.el5.img
""".strip()

# no configs
GRUB1_CONF_6 = """
title Red Hat Enterprise Linux Server
    kernel test
    module /2.6.18-194.8.1.el5.img
""".strip()

# too big default
GRUB1_CONF_7 = """
default = 1
title Red Hat Enterprise Linux Server (2.6.18-194.8.1.el5)
    kernel test
    module /2.6.18-194.8.1.el5.img
""".strip()

# only title
GRUB1_CONF_8 = """
title Red Hat Enterprise Linux Server (2.6.18-194.8.1.el5)
""".strip()

GRUB2_CFG_3 = """
menuentry 'Red Hat Enterprise Linux Server, with Linux 3.10.0-123.9.3.el7.x86_64' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-123.9.3.el7.x86_64-advanced-5a1c841f-5cfe-4d59-b3a0-4b788369d6cb' { load_video
    set gfxpayload=keep
    if [ x$feature_platform_search_hint = xy ]; then
      search --no-floppy --fs-uuid --set=root --hint-bios=hd0,msdos1 --hint-efi=hd0,msdos1 --hint-baremetal=ahci0,msdos1 --hint='hd0,msdos1'  93f2c0dc-6201-4d26-a610-4b3998983ea2
    else
      search --no-floppy --fs-uuid --set=root 93f2c0dc-6201-4d26-a610-4b3998983ea2
    fi
    linux16 /vmlinuz-3.10.0-123.9.3.el7.x86_64 root=UUID=5a1c841f-5cfe-4d59-b3a0-4b788369d6cb ro crashkernel=auto  vconsole.font=latarcyrheb-sun16 console=ttyS0,38400 rd.lvm.lv=VG_RACS-CCP/lv-rootfs vconsole.keymap=us LANG=en_US.UTF-8
    initrd16 /initramfs-3.10.0-123.9.3.el7.x86_64.img
}
""".strip()

GRUB2_CFG_4 = """
menuentry {
    linux16 /vmlinuz-3.10.0-123.9.3.el7.x86_64 crashkernel=auto
    initrd16 /initramfs-3.10.0-123.9.3.el7.x86_64.img
}
""".strip()

GRUB2_EDITENV_LIST = """
saved_entry=08c540cbca4d412c83e44a745aac36eb-4.18.0-80.1.2.el8_0.x86_64
kernelopts=root=/dev/mapper/rhel_vm37--146-root ro crashkernel=auto resume=/dev/mapper/rhel_vm37--146-swap rd.lvm.lv=rhel_vm37-146/root rd.lvm.lv=rhel_vm37-146/swap boot_success=0
boot_success=0
""".strip()


def test_grub_conf_1():
    expected_result = {'grub_kernels': ["vmlinuz-2.6.18-194.8.1.el5", "vmlinuz-2.6.18-194.17.1.el5"],
                       'grub_initrds': ["initrd-2.6.18-194.8.1.el5.img", "initramfs-2.6.18-194.8.1.el5.img"]}
    print(Grub1Config(context_wrap(GRUB1_CONF_3)).kernel_initrds)
    assert expected_result == Grub1Config(context_wrap(GRUB1_CONF_3)).kernel_initrds

    expected_result = {'grub_kernels': ["vmlinuz-2.6.18-194.8.1.el5"],
                       'grub_initrds': []}

    grub1 = Grub1Config(context_wrap(GRUB1_CONF_4))
    print(grub1)
    assert grub1.is_kdump_iommu_enabled is False
    assert expected_result == grub1.kernel_initrds
    print('-----')
    print(grub1.get_current_title())
    assert grub1.get_current_title() is None

    grub1 = Grub1Config(context_wrap(GRUB1_CONF_5))
    assert grub1.is_kdump_iommu_enabled is False
    print('-0')
    print(grub1.get_current_title())
    assert grub1.get_current_title() == {
            'title_name': '(2.6.18-194.8.1.el5)',
            'kernel': None, 'module': '/2.6.18-194.8.1.el5.img'}

    grub1 = Grub1Config(context_wrap(GRUB1_CONF_6))
    assert grub1.is_kdump_iommu_enabled is False
    assert grub1.get_current_title() == {
        'title_name': 'Red Hat Enterprise Linux Server',
        'kernel': 'test', 'module': '/2.6.18-194.8.1.el5.img'}

    grub1 = Grub1Config(context_wrap(GRUB1_CONF_7))
    assert grub1.is_kdump_iommu_enabled is False
    assert grub1.get_current_title() is None

    grub1 = Grub1Config(context_wrap(GRUB1_CONF_8))
    assert grub1.is_kdump_iommu_enabled is False

    grub1efi = Grub1EFIConfig(context_wrap(GRUB1_CONF_4))
    assert grub1efi.get_current_title() is None

    grub1efi = Grub1EFIConfig(context_wrap(GRUB1_CONF_5))
    assert grub1efi.get_current_title() == {
            'title_name': '(2.6.18-194.8.1.el5)',
            'kernel': None, 'module': '/2.6.18-194.8.1.el5.img'}

    grub1efi = Grub1EFIConfig(context_wrap(GRUB1_CONF_6))
    assert grub1efi.get_current_title() == {
        'title_name': 'Red Hat Enterprise Linux Server',
        'kernel': 'test', 'module': '/2.6.18-194.8.1.el5.img'}

    grub1efi = Grub1EFIConfig(context_wrap(GRUB1_CONF_7))
    assert grub1efi.get_current_title() is None

    grub_conf = Grub2Config(context_wrap(GRUB2_CFG_1))['menuentry']
    print(grub_conf)
    assert 'load_video' in grub_conf[0]
    assert 'load_env' not in grub_conf[0]
    assert 'insmod' in grub_conf[0]

    expected_result = {'grub_kernels': ["vmlinuz-3.10.0-229.el7.x86_64", "vmlinuz-3.10.0-123.13.2.el7.x86_64",
                                        "vmlinuz-3.10.0-123.el7.x86_64", "vmlinuz-0-rescue-13798ffcbc1ed4374f3f2e0fa6c923ad"],
                       'grub_initrds': ["initramfs-3.10.0-229.el7.x86_64.img", "initramfs-3.10.0-123.13.2.el7.x86_64.img",
                                        "initramfs-3.10.0-123.el7.x86_64.img", "initramfs-0-rescue-13798ffcbc1ed4374f3f2e0fa6c923ad.img"]}
    assert expected_result == Grub2Config(context_wrap(GRUB2_CFG_2)).kernel_initrds

    grub_conf = Grub2Config(context_wrap(GRUB2_CFG_3))
    assert 'load_video' not in grub_conf['menuentry'][0]
    assert grub_conf.is_kdump_iommu_enabled is False


def test_grub2_grubenv():
    grub_env = Grub2Grubenv(context_wrap(GRUB2_EDITENV_LIST))
    assert grub_env.name == '08c540cbca4d412c83e44a745aac36eb-4.18.0-80.1.2.el8_0.x86_64'
    assert 'crashkernel=auto' in grub_env.cmdline
    assert grub_env.kernelopts['ro'] == [True]
    assert grub_env.kernelopts['rd.lvm.lv'][0] == 'rhel_vm37-146/root'


def test_grub_conf_raise():
    with pytest.raises(Exception) as e:
        Grub2Config(context_wrap(GRUB2_CFG_4))
    assert "Cannot parse menuentry line: menuentry {" in str(e)
