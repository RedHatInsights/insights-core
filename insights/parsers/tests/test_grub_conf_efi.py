from insights.tests import context_wrap
from insights.parsers.grub_conf import Grub2EFIConfig

GRUB2_EFI_CFG = """
### BEGIN /etc/grub.d/10_linux ###
menuentry 'Red Hat Enterprise Linux Server (3.10.0-514.16.1.el7.x86_64) 7.3 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-514.el7.x86_64-advanced-9727cab4-12c2-41a8-9527-9644df34e586' {
    load_video
    set gfxpayload=keep
    insmod gzio
    insmod part_gpt
    insmod xfs
    set root='hd0,gpt2'
    if [ x$feature_platform_search_hint = xy ]; then
      search --no-floppy --fs-uuid --set=root --hint-bios=hd0,gpt2 --hint-efi=hd0,gpt2 --hint-baremetal=ahci0,gpt2  d80fa96c-ffa1-4894-9282-aeda37f0befe
    else
      search --no-floppy --fs-uuid --set=root d80fa96c-ffa1-4894-9282-aeda37f0befe
    fi
    linuxefi /vmlinuz-3.10.0-514.16.1.el7.x86_64 root=/dev/mapper/rhel-root ro rd.luks.uuid=luks-a40b320e-0711-4cd6-8f9e-ce32810e2a79 rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet LANG=en_US.UTF-8
    initrdefi /initramfs-3.10.0-514.16.1.el7.x86_64.img
}
menuentry 'Red Hat Enterprise Linux Server (3.10.0-514.10.2.el7.x86_64) 7.3 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-514.el7.x86_64-advanced-9727cab4-12c2-41a8-9527-9644df34e586' {
    load_video
    set gfxpayload=keep
    insmod gzio
    insmod part_gpt
    insmod xfs
    set root='hd0,gpt2'
    if [ x$feature_platform_search_hint = xy ]; then
      search --no-floppy --fs-uuid --set=root --hint-bios=hd0,gpt2 --hint-efi=hd0,gpt2 --hint-baremetal=ahci0,gpt2  d80fa96c-ffa1-4894-9282-aeda37f0befe
    else
      search --no-floppy --fs-uuid --set=root d80fa96c-ffa1-4894-9282-aeda37f0befe
    fi
    linuxefi /vmlinuz-3.10.0-514.10.2.el7.x86_64 root=/dev/mapper/rhel-root ro rd.luks.uuid=luks-a40b320e-0711-4cd6-8f9e-ce32810e2a79 rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet LANG=en_US.UTF-8
    initrdefi /initramfs-3.10.0-514.10.2.el7.x86_64.img
}
menuentry 'Red Hat Enterprise Linux Server (3.10.0-514.el7.x86_64) 7.3 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-514.el7.x86_64-advanced-9727cab4-12c2-41a8-9527-9644df34e586' {
    load_video
    set gfxpayload=keep
    insmod gzio
    insmod part_gpt
    insmod xfs
    set root='hd0,gpt2'
    if [ x$feature_platform_search_hint = xy ]; then
      search --no-floppy --fs-uuid --set=root --hint-bios=hd0,gpt2 --hint-efi=hd0,gpt2 --hint-baremetal=ahci0,gpt2  d80fa96c-ffa1-4894-9282-aeda37f0befe
    else
      search --no-floppy --fs-uuid --set=root d80fa96c-ffa1-4894-9282-aeda37f0befe
    fi
    linuxefi /vmlinuz-3.10.0-514.el7.x86_64 root=/dev/mapper/rhel-root ro rd.luks.uuid=luks-a40b320e-0711-4cd6-8f9e-ce32810e2a79 rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet LANG=en_US.UTF-8
    initrdefi /initramfs-3.10.0-514.el7.x86_64.img
}
menuentry 'Red Hat Enterprise Linux Server (0-rescue-f1340b5dd6ee4c26b587621566111421) 7.3 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-0-rescue-f1340b5dd6ee4c26b587621566111421-advanced-9727cab4-12c2-41a8-9527-9644df34e586' {
    load_video
    insmod gzio
    insmod part_gpt
    insmod xfs
    set root='hd0,gpt2'
    if [ x$feature_platform_search_hint = xy ]; then
      search --no-floppy --fs-uuid --set=root --hint-bios=hd0,gpt2 --hint-efi=hd0,gpt2 --hint-baremetal=ahci0,gpt2  d80fa96c-ffa1-4894-9282-aeda37f0befe
    else
      search --no-floppy --fs-uuid --set=root d80fa96c-ffa1-4894-9282-aeda37f0befe
    fi
    linuxefi /vmlinuz-0-rescue-f1340b5dd6ee4c26b587621566111421 root=/dev/mapper/rhel-root ro rd.luks.uuid=luks-a40b320e-0711-4cd6-8f9e-ce32810e2a79 rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet
    initrdefi /initramfs-0-rescue-f1340b5dd6ee4c26b587621566111421.img
}

### END /etc/grub.d/10_linux ###
""".strip()  # noqa


class TestGrub2EFI():
    def test_get_grub_kernel_initrd(self):
        expected = {'grub_kernels': ['vmlinuz-3.10.0-514.16.1.el7.x86_64',
                                     'vmlinuz-3.10.0-514.10.2.el7.x86_64',
                                     'vmlinuz-3.10.0-514.el7.x86_64',
                                     'vmlinuz-0-rescue-f1340b5dd6ee4c26b587621566111421'],
                    'grub_initrds': ['initramfs-3.10.0-514.16.1.el7.x86_64.img',
                                     'initramfs-3.10.0-514.10.2.el7.x86_64.img',
                                     'initramfs-3.10.0-514.el7.x86_64.img',
                                     'initramfs-0-rescue-f1340b5dd6ee4c26b587621566111421.img']}

        assert expected == Grub2EFIConfig((context_wrap(GRUB2_EFI_CFG))).kernel_initrds
