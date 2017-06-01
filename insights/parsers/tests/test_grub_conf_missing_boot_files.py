from insights.tests import context_wrap
from insights.parsers.grub_conf import Grub1Config, Grub2Config

# RHEL7
GRUB2_CFG_1 = """
## BEGIN /etc/grub.d/10_linux ###
menuentry 'Red Hat Enterprise Linux Server, with Linux 3.10.0-123.9.3.el7.x86_64' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-123.9.3.el7.x86_64-advanced-5a1c841f-5cfe-4d59-b3a0-4b788369d6cb' {
    load_video
    set gfxpayload=keep
    insmod gzio
    insmod part_msdos
    insmod ext2
    set root='hd0,msdos1'
    if [ x$feature_platform_search_hint = xy ]; then
      search --no-floppy --fs-uuid --set=root --hint-bios=hd0,msdos1 --hint-efi=hd0,msdos1 --hint-baremetal=ahci0,msdos1 --hint='hd0,msdos1'  93f2c0dc-6201-4d26-a610-4b3998983ea2
    else
      search --no-floppy --fs-uuid --set=root 93f2c0dc-6201-4d26-a610-4b3998983ea2
    fi
    linux16 /vmlinuz-3.10.0-123.9.3.el7.x86_64 root=UUID=5a1c841f-5cfe-4d59-b3a0-4b788369d6cb ro crashkernel=auto  vconsole.font=latarcyrheb-sun16 console=ttyS0,38400 rd.lvm.lv=VG_RACS-CCP/lv-rootfs vconsole.keymap=us LANG=en_US.UTF-8
    initrd16 /initramfs-3.10.0-123.9.3.el7.x86_64.img
}
menuentry 'Red Hat Enterprise Linux Server, with Linux 0-rescue-00c2fbfaa85544e48d6ca1d919fa2dd3' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-0-rescue-00c2fbfaa85544e48d6ca1d919fa2dd3-advanced-5a1c841f-5cfe-4d59-b3a0-4b788369d6cb' {
    load_video
    insmod gzio
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

LS_BOOT_1 = """
/boot:
total 68392
dr-xr-xr-x.  4 0 0     4096 Jan 12 17:45 .
drwxr-xr-x. 19 0 0     4096 Jan 13 19:49 ..
-rw-r--r--.  1 0 0      170 Oct 30 09:50 .vmlinuz-3.10.0-123.9.3.el7.x86_64.hmac
-rw-------.  1 0 0  2841475 Oct 30 09:50 System.map-3.10.0-123.9.3.el7.x86_64
-rw-r--r--.  1 0 0   122093 Oct 30 09:50 config-3.10.0-123.9.3.el7.x86_64
drwxr-xr-x.  6 0 0     4096 Jan 12 17:45 grub2
-rw-r--r--.  1 0 0 38922434 Jan 12 17:45 initramfs-0-rescue-00c2fbfaa85544e48d6ca1d919fa2dd3.img
-rw-r--r--.  1 0 0 17364252 Jan 12 17:45 initramfs-3.10.0-123.9.3.el7.x86_64.img
-rw-r--r--.  1 0 0   589451 Jan 12 17:45 initrd-plymouth.img
drwx------.  2 0 0    16384 Jan 12 17:38 lost+found
-rw-r--r--.  1 0 0   228621 Oct 30 09:52 symvers-3.10.0-123.9.3.el7.x86_64.gz
-rwxr-xr-x.  1 0 0  4904112 Jan 12 17:45 vmlinuz-0-rescue-00c2fbfaa85544e48d6ca1d919fa2dd3
-rwxr-xr-x.  1 0 0  4904112 Oct 30 09:50 vmlinuz-3.10.0-123.9.3.el7.x86_64
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

LS_BOOT_2 = """
/boot:
total 173260
dr-xr-xr-x.  3 0 0     4096 Mar 26 12:23 .
drwxr-xr-x. 17 0 0     4096 Mar 26 11:12 ..
-rw-r--r--.  1 0 0      171 Dec 13 10:54 .vmlinuz-3.10.0-123.13.2.el7.x86_64.hmac
-rw-r--r--.  1 0 0      166 May  6  2014 .vmlinuz-3.10.0-123.el7.x86_64.hmac
-rw-r--r--.  1 0 0      166 Jan 30 09:40 .vmlinuz-3.10.0-229.el7.x86_64.hmac
-rw-------.  1 0 0  2841409 Dec 13 10:54 System.map-3.10.0-123.13.2.el7.x86_64
-rw-------.  1 0 0  2840084 May  6  2014 System.map-3.10.0-123.el7.x86_64
-rw-------.  1 0 0  2881257 Jan 30 09:40 System.map-3.10.0-229.el7.x86_64
-rw-r--r--.  1 0 0   122094 Dec 13 10:54 config-3.10.0-123.13.2.el7.x86_64
-rw-r--r--.  1 0 0   122059 May  6  2014 config-3.10.0-123.el7.x86_64
-rw-r--r--.  1 0 0   123838 Jan 30 09:40 config-3.10.0-229.el7.x86_64
drwxr-xr-x.  6 0 0      104 Mar 26 12:05 grub2
-rw-r--r--.  1 0 0 40654410 Dec 22 14:48 initramfs-0-rescue-13798ffcbc1ed4374f3f2e0fa6c923ad.img
-rw-------.  1 0 0 16742742 Dec 22 15:36 initramfs-3.10.0-123.13.2.el7.x86_64.img
-rw-------.  1 0 0 18795253 Mar 26 12:02 initramfs-3.10.0-123.13.2.el7.x86_64kdump.img
-rw-------.  1 0 0 17246244 Dec 22 14:52 initramfs-3.10.0-123.el7.x86_64.img
-rw-------.  1 0 0 17111790 Dec 22 15:34 initramfs-3.10.0-123.el7.x86_64kdump.img
-rw-------.  1 0 0 18180132 Mar 26 12:05 initramfs-3.10.0-229.el7.x86_64.img
-rw-------.  1 0 0 18400548 Mar 26 12:23 initramfs-3.10.0-229.el7.x86_64kdump.img
-rw-r--r--.  1 0 0   867063 Mar 26 12:05 initrd-plymouth.img
-rw-r--r--.  1 0 0   228603 Dec 13 10:55 symvers-3.10.0-123.13.2.el7.x86_64.gz
-rw-r--r--.  1 0 0   228562 May  6  2014 symvers-3.10.0-123.el7.x86_64.gz
-rw-r--r--.  1 0 0   240039 Jan 30 09:44 symvers-3.10.0-229.el7.x86_64.gz
-rwxr-xr-x.  1 0 0  4902000 Dec 22 14:48 vmlinuz-0-rescue-13798ffcbc1ed4374f3f2e0fa6c923ad
-rwxr-xr-x.  1 0 0  4904688 Dec 13 10:54 vmlinuz-3.10.0-123.13.2.el7.x86_64
-rwxr-xr-x.  1 0 0  4902000 May  6  2014 vmlinuz-3.10.0-123.el7.x86_64
-rwxr-xr-x.  1 0 0  5026624 Jan 30 09:40 vmlinuz-3.10.0-229.el7.x86_64
""".strip()

# RHEL5/6
GRUB_CONF_3 = """
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
    initrd /initrd-2.6.18-194.17.1.el5.img
""".strip()

# Kernel and initrd referenced in grub.conf are actually softlinks to other files
GRUB_CONF_LINKS = """
title Linux (Logical Disk 0)
        root (hd0,0)
        kernel /boot/vmlinuz ro root=LABEL=/root LANG=en_US.UTF-8 SYSFONT=latarcyrheb-sun16 KEYBOARDTYPE=pc KEYTABLE=us crashkernel=768M  rd_NO_PLYMOUTH nodmraid
        initrd /boot/initrd
""".strip()
# Xen configs look a little different in grub.conf
GRUB_CONF_XEN = """
title Red Hat Enterprise Linux Server (2.6.18-398.el5xen)
    root (hd0,0)
    kernel /xen.gz-2.6.18-398.el5
    module /vmlinuz-2.6.18-398.el5xen ro root=/dev/sda2
    module /initrd-2.6.18-398.el5xen.img
""".strip()
# Some machines PXE boot so don't check them because we can't know if they will work or not
GRUB_CONF_IPXE = """
title iPXE
  root (hd0,0)
  kernel (hd0,0)/boot/ipxe.lkrn
""".strip()


class TestGrub1ConfMissingBootFiles():
    def test_get_grub_kernel_initrd(self):
        expected_result = {'grub_kernels': ["vmlinuz-2.6.18-194.8.1.el5", "vmlinuz-2.6.18-194.17.1.el5"],
                           'grub_initrds': ["initrd-2.6.18-194.8.1.el5.img", "initrd-2.6.18-194.17.1.el5.img"]}
        assert expected_result == Grub1Config(context_wrap(GRUB_CONF_3)).kernel_initrds

        # Process grub.conf where kernel and initrd are softlinks
        expected_result = {'grub_kernels': ['vmlinuz'], 'grub_initrds': ['initrd']}
        assert expected_result == Grub1Config(context_wrap(GRUB_CONF_LINKS)).kernel_initrds

        # Process grub.conf from a Xen hypervisor
        expected_result = {'grub_kernels': ['vmlinuz-2.6.18-398.el5xen'], 'grub_initrds': ['initrd-2.6.18-398.el5xen.img']}
        assert expected_result == Grub1Config(context_wrap(GRUB_CONF_XEN)).kernel_initrds

        # Simulate grub.conf not containing any kernel or initrd entries
        expected_result = {'grub_kernels': [], 'grub_initrds': []}
        assert expected_result == Grub1Config(context_wrap(LS_BOOT_1)).kernel_initrds
        assert expected_result, Grub1Config(context_wrap(LS_BOOT_2)).kernel_initrds

        # Ignore grub.conf from machines that have PXE boot entries because we can't know if they are ok or not
        assert Grub1Config(context_wrap(GRUB_CONF_IPXE)).kernel_initrds == {}


class TestGrub2ConfMissingBootFiles():
    def test_get_grub_kernel_initrd(self):
        expected_result = {'grub_kernels': ["vmlinuz-3.10.0-123.9.3.el7.x86_64", "vmlinuz-0-rescue-00c2fbfaa85544e48d6ca1d919fa2dd3"],
                           'grub_initrds': ["initramfs-3.10.0-123.9.3.el7.x86_64.img", "initramfs-0-rescue-00c2fbfaa85544e48d6ca1d919fa2dd3.img"]}
        assert expected_result == Grub2Config((context_wrap(GRUB2_CFG_1))).kernel_initrds == expected_result
        expected_result = {'grub_kernels': ["vmlinuz-3.10.0-229.el7.x86_64", "vmlinuz-3.10.0-123.13.2.el7.x86_64",
                                            "vmlinuz-3.10.0-123.el7.x86_64", "vmlinuz-0-rescue-13798ffcbc1ed4374f3f2e0fa6c923ad"],
                           'grub_initrds': ["initramfs-3.10.0-229.el7.x86_64.img", "initramfs-3.10.0-123.13.2.el7.x86_64.img",
                                            "initramfs-3.10.0-123.el7.x86_64.img", "initramfs-0-rescue-13798ffcbc1ed4374f3f2e0fa6c923ad.img"]}
        assert expected_result == Grub2Config(context_wrap(GRUB2_CFG_2)).kernel_initrds

        # Simulate grub.conf not containing any kernel or initrd entries
        expected_result = {'grub_kernels': [], 'grub_initrds': []}
        assert expected_result == Grub2Config(context_wrap(LS_BOOT_1)).kernel_initrds
        assert expected_result, Grub2Config(context_wrap(LS_BOOT_2)).kernel_initrds
