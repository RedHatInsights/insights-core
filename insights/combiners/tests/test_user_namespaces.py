from ..user_namespaces import UserNamespaces
from ...parsers.cmdline import CmdLine
from ...parsers.grub_conf import Grub2Config
from ...tests import context_wrap

ENABLE_TOK_A = '''
user_namespaces.enable=1
'''.strip()  # noqa

ENABLE_TOK_B = '''
user-namespaces.enable=1
'''.strip()  # noqa

CMDLINE = '''
BOOT_IMAGE=/vmlinuz-3.10.0-514.6.1.el7.x86_64 root=/dev/mapper/rhel-root ro crashkernel=auto rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap {0}
'''.strip()  # noqa

GRUB2_CONF = '''
### BEGIN /etc/grub.d/10_linux ###
menuentry 'Red Hat Enterprise Linux Server (3.10.0-514.16.1.el7.x86_64) 7.3 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-514.el7.x86_64-advanced-9727cab4-12c2-41a8-9527-9644df34e586' {{
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
        linuxefi /vmlinuz-3.10.0-514.16.1.el7.x86_64 root=/dev/mapper/rhel-root ro rd.luks.uuid=luks-a40b320e-0711-4cd6-8f9e-ce32810e2a79 rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet LANG=en_US.UTF-8 {0}
        initrdefi /initramfs-3.10.0-514.16.1.el7.x86_64.img
}}
menuentry 'Red Hat Enterprise Linux Server (3.10.0-514.10.2.el7.x86_64) 7.3 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-514.el7.x86_64-advanced-9727cab4-12c2-41a8-9527-9644df34e586' {{
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
        linuxefi /vmlinuz-3.10.0-514.10.2.el7.x86_64 root=/dev/mapper/rhel-root ro rd.luks.uuid=luks-a40b320e-0711-4cd6-8f9e-ce32810e2a79 rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet LANG=en_US.UTF-8 {1}
        initrdefi /initramfs-3.10.0-514.10.2.el7.x86_64.img
}}
'''  # noqa

MENUENTRY_0 = '''
'Red Hat Enterprise Linux Server (3.10.0-514.16.1.el7.x86_64) 7.3 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-514.el7.x86_64-advanced-9727cab4-12c2-41a8-9527-9644df34e586'
'''.strip()  # noqa

MENUENTRY_1 = '''
'Red Hat Enterprise Linux Server (3.10.0-514.10.2.el7.x86_64) 7.3 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-514.el7.x86_64-advanced-9727cab4-12c2-41a8-9527-9644df34e586'
'''.strip()  # noqa

CASES = [
        # noqa
        # |-- provided --|  |---- expected results ---|
        # ((cmdline, grub), (enabled, enabled_configs))
        # Not enabled, no grub data
        ((CMDLINE.format(''), None), (False, [])),
        # Not enabled, not enabled in grub
        ((CMDLINE.format(''), GRUB2_CONF.format('', '')), (False, [])),
        # Not enabled, but enabled in menuentry 1
        ((CMDLINE.format(''), GRUB2_CONF.format('', ENABLE_TOK_A)),
         (False, [MENUENTRY_1])),
        # Enabled, no grub data
        ((CMDLINE.format(ENABLE_TOK_A), None), (True, [])),
        # Enabled, but not enabled in grub
        ((CMDLINE.format(ENABLE_TOK_A), GRUB2_CONF.format('', '')),
         (True, [])),
        # Enabled, enabled in menuentry 0
        ((CMDLINE.format(ENABLE_TOK_A), GRUB2_CONF.format(ENABLE_TOK_A, '')),
         (True, [MENUENTRY_0])),
        # Dash syntax, rather than underscore
        ((CMDLINE.format(ENABLE_TOK_B), GRUB2_CONF.format(ENABLE_TOK_B, '')),
         (True, [MENUENTRY_0]))
        ]


def test_integration():
    for case in CASES:
        context = {}
        context[CmdLine] = CmdLine(context_wrap(case[0][0]))
        if case[0][1] is not None:
            context[Grub2Config] = Grub2Config(context_wrap(case[0][1]))

        un = UserNamespaces(context.get(CmdLine), context.get(Grub2Config))
        assert un.enabled() == case[1][0]
        assert un.enabled_configs() == case[1][1]
