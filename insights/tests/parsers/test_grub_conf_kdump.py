from insights.parsers.grub_conf import Grub1Config, Grub2Config
from insights.tests import context_wrap

BAD_DEFAULT_1 = """
#boot=/dev/sda

default=${last}
timeout=0
splashimage=(hd0,0)/grub/splash.xpm.gz
hiddenmenu
title Red Hat Enterprise Linux Server (2.6.32-431.11.2.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.11.2.el6.x86_64 crashkernel=128M@8M rhgb quiet
""".strip()

GOOD_OFFSET_4 = """
#boot=/dev/sda

default=1
timeout=0
splashimage=(hd0,0)/grub/splash.xpm.gz
hiddenmenu
title Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.17.1.el6.x86_64 crashkernel=  rhgb quiet
title Red Hat Enterprise Linux Server (2.6.32-431.11.2.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.11.2.el6.x86_64 crashkernel=128M@32M rhgb quiet
""".strip()

GOOD_OFFSET_3 = """
#boot=/dev/sda
default=1
timeout=0
splashimage=(hd0,0)/grub/splash.xpm.gz
hiddenmenu
title Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.17.1.el6.x86_64 crashkernel=128M@0  rhgb quiet
title Red Hat Enterprise Linux Server (2.6.32-431.11.2.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.11.2.el6.x86_64 crashkernel=128M@0 rhgb quiet
""".strip()

GOOD_OFFSET_2 = """
#boot=/dev/sda

default=1
timeout=0
splashimage=(hd0,0)/grub/splash.xpm.gz
hiddenmenu
title Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.17.1.el6.x86_64 crashkernel=128M@0M  rhgb quiet
title Red Hat Enterprise Linux Server (2.6.32-431.11.2.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.11.2.el6.x86_64 crashkernel=128M@0M rhgb quiet
""".strip()

GOOD_OFFSET_1 = """
#boot=/dev/sda
default=0
timeout=0
splashimage=(hd0,0)/grub/splash.xpm.gz
hiddenmenu
title Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.17.1.el6.x86_64 crashkernel=128M rhgb quiet
title Red Hat Enterprise Linux Server (2.6.32-431.11.2.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.11.2.el6.x86_64 crashkernel=128M rhgb quiet
""".strip()

BAD_OFFSET = """
#boot=/dev/sda

default=1
timeout=0
splashimage=(hd0,0)/grub/splash.xpm.gz
hiddenmenu
title Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.17.1.el6.x86_64 crashkernel=  rhgb quiet
title Red Hat Enterprise Linux Server (2.6.32-431.11.2.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.11.2.el6.x86_64 crashkernel=128M@16M rhgb quiet
""".strip()

NOMATCH_MEMORY = """
#boot=/dev/sda
default=1
timeout=0
splashimage=(hd0,0)/grub/splash.xpm.gz
hiddenmenu
title Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.17.1.el6.x86_64 rhgb quiet
title Red Hat Enterprise Linux Server (2.6.32-431.11.2.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.11.2.el6.x86_64 crashkernel=128M@M rhgb quiet
""".strip()

NOMATCH_CRASH_PARAM = """
#boot=/dev/sda
default=1
timeout=0
splashimage=(hd0,0)/grub/splash.xpm.gz
hiddenmenu
title Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.17.1.el6.x86_64 rhgb quiet
title Red Hat Enterprise Linux Server (2.6.32-431.11.2.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.11.2.el6.x86_64 rhgb quiet
""".strip()

IOMMU_OFF = """
title Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64)
    kernel /vmlinuz-2.6.32-279.el6.x86_64 ro root=/dev/mapper/vg00-lv00 intel_iommu=off rd_LVM_LV=vg00/lv00 crashkernel=256M@16M
"""
IOMMU_MISSING = """
title Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64)
    kernel /vmlinuz-2.6.32-279.el6.x86_64 ro root=/dev/mapper/vg00-lv00 rd_LVM_LV=vg00/lv00 crashkernel=256M@16M
"""
IOMMU_ON = """
title Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64)
    kernel /vmlinuz-2.6.32-279.el6.x86_64 ro root=/dev/mapper/vg00-lv00 intel_iommu=on rd_LVM_LV=vg00/lv00 crashkernel=256M@16M
"""

IOMMU2_OFF = """
menuentry 'Red Hat Enterprise Linux Workstation (3.10.0-327.36.3.el7.x86_64) 7.2 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-123.13.2.el7.x86_64-advanced-fbff9f50-62c3-484e-bca5-d53f672cda7c' {
    linux16 /vmlinuz-3.10.0-327.36.3.el7.x86_64 root=/dev/RHEL7CSB/Root ro rd.lvm.lv=RHEL7CSB/Root rd.luks.uuid=luks-96c66446-77fd-4431-9508-f6912bd84194 intel_iommu=off crashkernel=128M@16M rd.lvm.lv=RHEL7CSB/Swap vconsole.font=latarcyrheb-sun16 rhgb quiet LANG=en_GB.utf8
    initrd16 /initramfs-3.10.0-327.36.3.el7.x86_64.img
}
"""
IOMMU2_MISSING = """
menuentry 'Red Hat Enterprise Linux Workstation (3.10.0-327.36.3.el7.x86_64) 7.2 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-123.13.2.el7.x86_64-advanced-fbff9f50-62c3-484e-bca5-d53f672cda7c' {
    linux16 /vmlinuz-3.10.0-327.36.3.el7.x86_64 root=/dev/RHEL7CSB/Root ro rd.lvm.lv=RHEL7CSB/Root rd.luks.uuid=luks-96c66446-77fd-4431-9508-f6912bd84194 crashkernel=128M@16M rd.lvm.lv=RHEL7CSB/Swap vconsole.font=latarcyrheb-sun16 rhgb quiet LANG=en_GB.utf8
    initrd16 /initramfs-3.10.0-327.36.3.el7.x86_64.img
}
"""
IOMMU2_ON = """
menuentry 'Red Hat Enterprise Linux Workstation (3.10.0-327.36.3.el7.x86_64) 7.2 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-123.13.2.el7.x86_64-advanced-fbff9f50-62c3-484e-bca5-d53f672cda7c' {
    linux16 /vmlinuz-3.10.0-327.36.3.el7.x86_64 root=/dev/RHEL7CSB/Root ro rd.lvm.lv=RHEL7CSB/Root rd.luks.uuid=luks-96c66446-77fd-4431-9508-f6912bd84194 intel_iommu=on crashkernel=128M@16M rd.lvm.lv=RHEL7CSB/Swap vconsole.font=latarcyrheb-sun16 rhgb quiet LANG=en_GB.utf8
    initrd16 /initramfs-3.10.0-327.36.3.el7.x86_64.img
}
"""

GRUB2_CONFIG = """
### BEGIN /etc/grub.d/00_header ###
set pager=1
/
if [ -s $prefix/grubenv ]; then
  load_env
fi
#[...]
if [ x"${feature_menuentry_id}" = xy ]; then
  menuentry_id_option="--id"
else
  menuentry_id_option=""
fi
#[...]
### BEGIN /etc/grub.d/10_linux ###
menuentry 'Red Hat Enterprise Linux Workstation (3.10.0-327.36.3.el7.x86_64) 7.2 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-123.13.2.el7.x86_64-advanced-fbff9f50-62c3-484e-bca5-d53f672cda7c' {
    load_video
    set gfxpayload=keep
    insmod gzio
    insmod part_msdos
    insmod ext2
    set root='hd0,msdos1'
    if [ x$feature_platform_search_hint = xy ]; then
      search --no-floppy --fs-uuid --set=root --hint-bios=hd0,msdos1 --hint-efi=hd0,msdos1 --hint-baremetal=ahci0,msdos1 --hint='hd0,msdos1'  1184ab74-77b5-4cfa-81d3-fb87b0457577
    else
      search --no-floppy --fs-uuid --set=root 1184ab74-77b5-4cfa-81d3-fb87b0457577
    fi
    linux16 /vmlinuz-3.10.0-327.36.3.el7.x86_64 root=/dev/RHEL7CSB/Root ro rd.lvm.lv=RHEL7CSB/Root rd.luks.uuid=luks-96c66446-77fd-4431-9508-f6912bd84194 crashkernel=128M@16M rd.lvm.lv=RHEL7CSB/Swap vconsole.font=latarcyrheb-sun16 rhgb quiet LANG=en_GB.utf8
    initrd16 /initramfs-3.10.0-327.36.3.el7.x86_64.img
}
menuentry 'Red Hat Enterprise Linux Workstation (3.10.0-267.el7.x86_64) 7.1 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-123.13.2.el7.x86_64-advanced-fbff9f50-62c3-484e-bca5-d53f672cda7c' {
    load_video
    set gfxpayload=keep
    insmod gzio
    insmod part_msdos
    insmod ext2
    set root='hd0,msdos1'
    if [ x$feature_platform_search_hint = xy ]; then
      search --no-floppy --fs-uuid --set=root --hint-bios=hd0,msdos1 --hint-efi=hd0,msdos1 --hint-baremetal=ahci0,msdos1 --hint='hd0,msdos1'  1184ab74-77b5-4cfa-81d3-fb87b0457577
    else
      search --no-floppy --fs-uuid --set=root 1184ab74-77b5-4cfa-81d3-fb87b0457577
    fi
    linux16 /vmlinuz-3.10.0-267.el7.x86_64 root=/dev/RHEL7CSB/Root ro rd.lvm.lv=RHEL7CSB/Root rd.luks.uuid=luks-96c66446-77fd-4431-9508-f6912bd84194 crashkernel=auto  vconsole.keymap=us rd.lvm.lv=RHEL7CSB/Swap vconsole.font=latarcyrheb-sun16 rhgb quiet LANG=en_GB.utf8
    initrd16 /initramfs-3.10.0-267.el7.x86_64.img
}
menuentry 'Red Hat Enterprise Linux Workstation (3.10.0-230.el7synaptics.1186112.1186106.2.x86_64) 7.1 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-123.13.2.el7.x86_64-advanced-fbff9f50-62c3-484e-bca5-d53f672cda7c' {
    load_video
    set gfxpayload=keep
    insmod gzio
    insmod part_msdos
    insmod ext2
    set root='hd0,msdos1'
    if [ x$feature_platform_search_hint = xy ]; then
      search --no-floppy --fs-uuid --set=root --hint-bios=hd0,msdos1 --hint-efi=hd0,msdos1 --hint-baremetal=ahci0,msdos1 --hint='hd0,msdos1'  1184ab74-77b5-4cfa-81d3-fb87b0457577
    else
      search --no-floppy --fs-uuid --set=root 1184ab74-77b5-4cfa-81d3-fb87b0457577
    fi
    linux16 /vmlinuz-3.10.0-230.el7synaptics.1186112.1186106.2.x86_64 root=/dev/RHEL7CSB/Root ro rd.lvm.lv=RHEL7CSB/Root rd.luks.uuid=luks-96c66446-77fd-4431-9508-f6912bd84194 crashkernel=auto  vconsole.keymap=us rd.lvm.lv=RHEL7CSB/Swap vconsole.font=latarcyrheb-sun16 rhgb quiet LANG=en_US.UTF-8
    initrd16 /initramfs-3.10.0-230.el7synaptics.1186112.1186106.2.x86_64.img
}
menuentry 'Red Hat Enterprise Linux Workstation, with Linux 0-rescue-71483baa33934d94a7804a398fed6241' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-0-rescue-71483baa33934d94a7804a398fed6241-advanced-fbff9f50-62c3-484e-bca5-d53f672cda7c' {
    load_video
    insmod gzio
    insmod part_msdos
    insmod ext2
    set root='hd0,msdos1'
    if [ x$feature_platform_search_hint = xy ]; then
      search --no-floppy --fs-uuid --set=root --hint-bios=hd0,msdos1 --hint-efi=hd0,msdos1 --hint-baremetal=ahci0,msdos1 --hint='hd0,msdos1'  1184ab74-77b5-4cfa-81d3-fb87b0457577
    else
      search --no-floppy --fs-uuid --set=root 1184ab74-77b5-4cfa-81d3-fb87b0457577
    fi
    linux16 /vmlinuz-0-rescue-71483baa33934d94a7804a398fed6241 root=UUID=fbff9f50-62c3-484e-bca5-d53f672cda7c ro rd.lvm.lv=RHEL7CSB/Root rd.luks.uuid=luks-96c66446-77fd-4431-9508-f6912bd84194 crashkernel=auto  vconsole.keymap=us rd.lvm.lv=RHEL7CSB/Swap vconsole.font=latarcyrheb-sun16 rhgb quiet
    initrd16 /initramfs-0-rescue-71483baa33934d94a7804a398fed6241.img
}

"""


MODULE_TEST = """
### BEGIN /etc/grub.d/00_header ###
set pager=1
/
if [ -s $prefix/grubenv ]; then
  load_env
fi
#[...]
if [ x"${feature_menuentry_id}" = xy ]; then
  menuentry_id_option="--id"
else
  menuentry_id_option=""
fi
#[...]
### BEGIN /etc/grub.d/10_linux ###
menuentry 'Red Hat Enterprise Linux Workstation (3.10.0-327.36.3.el7.x86_64) 7.2 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-123.13.2.el7.x86_64-advanced-fbff9f50-62c3-484e-bca5-d53f672cda7c' {
    load_video
    set gfxpayload=keep
    insmod gzio
    insmod part_msdos
    insmod ext2
    set root='hd0,msdos1'
    if [ x$feature_platform_search_hint = xy ]; then
      search --no-floppy --fs-uuid --set=root --hint-bios=hd0,msdos1 --hint-efi=hd0,msdosyy1 --hint-baremetal=ahci0,msdos1 --hint='hd0,msdos1'  1184ab74-77b5-4cfa-81d3-fb87b0457577
    else
      search --no-floppy --fs-uuid --set=root 1184ab74-77b5-4cfa-81d3-fb87b0457577
    fi
    linux16 /vmlinuz-3.10.0-327.36.3.el7.x86_64 root=/dev/RHEL7CSB/Root ro rd.lvm.lv=RHEL7CSB/Root rd.luks.uuid=luks-96c66446-77fd-4431-9508-f6912bd84194 crashkernel=128M@16M rd.lvm.lv=RHEL7CSB/Swap vconsole.font=latarcyrheb-sun16 rhgb quiet LANG=en_GB.utf8
    initrd16 /initramfs-3.10.0-327.36.3.el7.x86_64.img
"""


def test_mod_internal():
    config = Grub2Config(context_wrap(MODULE_TEST))
    assert config
    assert type(config.kernel_initrds) is dict
    # Why is this two separate lists and not a list of dicts?
    assert 'grub_initrds' in config.kernel_initrds
    assert config.kernel_initrds['grub_initrds'] == ['initramfs-3.10.0-327.36.3.el7.x86_64.img']
    assert 'grub_kernels' in config.kernel_initrds
    assert config.kernel_initrds['grub_kernels'] == ['vmlinuz-3.10.0-327.36.3.el7.x86_64']


def test_kdump_iommu_enabled():
    assert Grub1Config(context_wrap(IOMMU_OFF)).is_kdump_iommu_enabled is False
    assert Grub1Config(context_wrap(IOMMU_MISSING)).is_kdump_iommu_enabled is False
    assert Grub1Config(context_wrap(IOMMU_ON)).is_kdump_iommu_enabled is True
    assert Grub2Config(context_wrap(IOMMU2_OFF)).is_kdump_iommu_enabled is False
    assert Grub2Config(context_wrap(IOMMU2_MISSING)).is_kdump_iommu_enabled is False
    assert Grub2Config(context_wrap(IOMMU2_ON)).is_kdump_iommu_enabled is True


"""
#boot=/dev/sda
default 0
timeout=0
splashimage=(hd0,0)/grub/splash.xpm.gz
hiddenmenu
title Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.17.1.el6.x86_64 crashkernel=128M rhgb quiet
title Red Hat Enterprise Linux Server (2.6.32-431.11.2.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.11.2.el6.x86_64 crashkernel=128M rhgb quiet
"""


def test_grub1_config():
    config = Grub1Config(context_wrap(GOOD_OFFSET_1))
    assert config
    assert 'configs' in config
    assert 'title' in config
    assert 'menuentry' not in config

    assert len(config['configs']) == 4
    assert config['configs']['default'] == ['0']
    assert config['configs']['timeout'] == ['0']
    assert config['configs']['splashimage'] == ['(hd0,0)/grub/splash.xpm.gz']
    assert config['configs']['hiddenmenu'] == ['']

    assert len(config['title']) == 2
    assert len(config['title'][0]) == 2
    assert config['title'][0]['title'] == 'Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64)'
    assert config['title'][0]['kernel'][0] == '/vmlinuz-2.6.32-431.17.1.el6.x86_64 crashkernel=128M rhgb quiet'
    assert len(config['title'][1]) == 2
    assert config['title'][1]['title'] == 'Red Hat Enterprise Linux Server (2.6.32-431.11.2.el6.x86_64)'
    assert config['title'][1]['kernel'][-1] == '/vmlinuz-2.6.32-431.11.2.el6.x86_64 crashkernel=128M rhgb quiet'

    assert config.is_kdump_iommu_enabled is False
    assert type(config.kernel_initrds) is dict
    # Why is this two separate lists and not a list of dicts?
    # Because this config has been deliberately cut down and is not a
    # real GRUB configuration, it can't find the initrds.
    assert 'grub_initrds' in config.kernel_initrds
    assert config.kernel_initrds['grub_initrds'] == []
    assert 'grub_kernels' in config.kernel_initrds
    assert config.kernel_initrds['grub_kernels'] == [
        'vmlinuz-2.6.32-431.17.1.el6.x86_64',
        'vmlinuz-2.6.32-431.11.2.el6.x86_64'
    ]


def test_grub2_config():
    config = Grub2Config(context_wrap(GRUB2_CONFIG))
    assert config
    assert 'configs' in config
    assert 'title' not in config
    assert 'menuentry' in config

    # Current parsing code is near useless for pulling information out of
    # GRUB2 config, as the file is actually a bash script.  So here we
    # don't do any testing of the junk in 'configs'.
    assert len(config['configs']) > 0

    assert len(config['menuentry']) == 4
    """
    menuentry 'Red Hat Enterprise Linux Workstation (3.10.0-327.36.3.el7.x86_64) 7.2 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-123.13.2.el7.x86_64-advanced-fbff9f50-62c3-484e-bca5-d53f672cda7c' {
        load_video
        set gfxpayload=keep
        insmod gzio
        insmod part_msdos
        insmod ext2
        set root='hd0,msdos1'
        if [ x$feature_platform_search_hint = xy ]; then
          search --no-floppy --fs-uuid --set=root --hint-bios=hd0,msdos1 --hint-efi=hd0,msdos1 --hint-baremetal=ahci0,msdos1 --hint='hd0,msdos1'  1184ab74-77b5-4cfa-81d3-fb87b0457577
        else
          search --no-floppy --fs-uuid --set=root 1184ab74-77b5-4cfa-81d3-fb87b0457577
        fi
        linux16 /vmlinuz-3.10.0-327.36.3.el7.x86_64 root=/dev/RHEL7CSB/Root ro rd.lvm.lv=RHEL7CSB/Root rd.luks.uuid=luks-96c66446-77fd-4431-9508-f6912bd84194 crashkernel=auto  vconsole.keymap=us rd.lvm.lv=RHEL7CSB/Swap vconsole.font=latarcyrheb-sun16 rhgb quiet LANG=en_GB.utf8
        initrd16 /initramfs-3.10.0-327.36.3.el7.x86_64.img
    }
    """
    # The current parsing code does a very bad job of reading menu
    # entry configuration.  Test a few things but we hope for better.
    assert len(config['menuentry'][0]) == 6
    assert config['menuentry'][0]['menuentry'] == "'Red Hat Enterprise Linux Workstation (3.10.0-327.36.3.el7.x86_64) 7.2 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-123.13.2.el7.x86_64-advanced-fbff9f50-62c3-484e-bca5-d53f672cda7c'"
    assert config['menuentry'][0]['load_video'] == ['']
    assert config['menuentry'][0]['initrd16'] == ['/initramfs-3.10.0-327.36.3.el7.x86_64.img']

    assert type(config.kernel_initrds) is dict
    assert 'grub_initrds' in config.kernel_initrds
    assert config.kernel_initrds['grub_initrds'] == [
        'initramfs-3.10.0-327.36.3.el7.x86_64.img',
        'initramfs-3.10.0-267.el7.x86_64.img',
        'initramfs-3.10.0-230.el7synaptics.1186112.1186106.2.x86_64.img',
        'initramfs-0-rescue-71483baa33934d94a7804a398fed6241.img'
    ]
    assert 'grub_kernels' in config.kernel_initrds
    assert config.kernel_initrds['grub_kernels'] == [
        'vmlinuz-3.10.0-327.36.3.el7.x86_64',
        'vmlinuz-3.10.0-267.el7.x86_64',
        'vmlinuz-3.10.0-230.el7synaptics.1186112.1186106.2.x86_64',
        'vmlinuz-0-rescue-71483baa33934d94a7804a398fed6241'
    ]
