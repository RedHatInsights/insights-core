from collections import namedtuple
from insights.combiners.ipv6 import IPv6
from insights.parsers.cmdline import CmdLine
from insights.parsers.lsmod import LsMod
from insights.parsers.modprobe import ModProbe
from insights.parsers.sysctl import Sysctl
from insights.parsers.uname import Uname
from insights.tests import context_wrap

Case = namedtuple('Case', ['cmdline', 'lsmod', 'modprobe', 'sysctl'])

UNAME_RHEL7 = '''
Linux localhost.localdomain 3.10.0-514.6.1.el7.x86_64 #1 SMP Sat Dec 10 11:15:38 EST 2016 x86_64 x86_64 x86_64 GNU/Linux
'''  # noqa

UNAME_RHEL6 = '''
Linux localhost.localdomain 2.6.32-642.el6.x86_64 #1 SMP Wed Apr 13 00:51:26 EDT 2016 x86_64 x86_64 x86_64 GNU/Linux
'''  # noqa

CMDLINE_DISABLED = '''
BOOT_IMAGE=/vmlinuz-3.10.0-514.6.1.el7.x86_64 root=/dev/mapper/rhel-root ro crashkernel=auto rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap ipv6.disable=1
'''  # noqa

CMDLINE_NOT_DISABLED = '''
BOOT_IMAGE=/vmlinuz-3.10.0-514.6.1.el7.x86_64 root=/dev/mapper/rhel-root ro crashkernel=auto rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap
'''  # noqa

CMDLINE_RHEL6_DISABLED = '''
ro root=/dev/mapper/VolGroup-lv_root rd_NO_LUKS LANG=en_US.UTF-8 rd_NO_MD rd_LVM_LV=VolGroup/lv_swap SYSFONT=latarcyrheb-sun16  rd_LVM_LV=VolGroup/lv_root  KEYBOARDTYPE=pc KEYTABLE=us rd_NO_DM rhgb quiet ipv6.disable=1
'''  # noqa

LSMOD_LOADED = '''
Module                  Size  Used by
vboxsf                 37955  1 
ipv6                  336282  12 
i2c_piix4              11232  0 
i2c_core               29132  1 i2c_piix4
snd_intel8x0           30524  0 
'''  # noqa

LSMOD_NOT_LOADED = '''
Module                  Size  Used by
vboxsf                 37955  1 
i2c_piix4              11232  0 
i2c_core               29132  1 i2c_piix4
snd_intel8x0           30524  0 
'''  # noqa

MODPROBE_NOT_DISABLED = '''
# framebuffer drivers
blacklist aty128fb
blacklist atyfb
blacklist radeonfb
blacklist i810fb
blacklist cirrusfb
blacklist intelfb
'''  # noqa

MODPROBE_DISABLED = '''
blacklist radeonfb
blacklist i810fb
blacklist cirrusfb
blacklist intelfb
options ipv6 disable=1
'''  # noqa

MODPROBE_FAKE = '''
blacklist radeonfb
blacklist i810fb
blacklist cirrusfb
blacklist intelfb
install ipv6 /bin/true
install blarfl /bin/true
'''  # noqa

MODPROBE_FAKE_COMMENTED = '''
blacklist radeonfb
blacklist i810fb
blacklist cirrusfb
blacklist intelfb
# install ipv6 /bin/true
'''  # noqa

SYSCTL_DISABLED = '''
net.ipv6.conf.all.disable_ipv6 = 1
'''  # noqa

SYSCTL_NOT_DISABLED = '''
net.ipv6.route.gc_elasticity = 9
net.ipv6.route.gc_interval = 30
net.ipv6.route.gc_min_interval = 0
net.ipv6.route.gc_min_interval_ms = 500
net.ipv6.route.gc_thresh = 1024
net.ipv6.route.gc_timeout = 60
'''  # noqa

CASES = [
    # noqa
    # RHEL7 not disabled
    (7, Case(CMDLINE_NOT_DISABLED, None, None, SYSCTL_NOT_DISABLED),
        (False, set())),
    # RHEL7 disabled via cmdline
    (7, Case(CMDLINE_DISABLED, None, None, SYSCTL_NOT_DISABLED),
        (True, set(['cmdline']))),
    # RHEL7 disabled via sysctl
    (7, Case(CMDLINE_NOT_DISABLED, None, None, SYSCTL_DISABLED),
        (True, set(['sysctl']))),
    # RHEL7 disabled by both cmdline and sysctl
    (7, Case(CMDLINE_DISABLED, None, None, SYSCTL_DISABLED),
        (True, set(['cmdline', 'sysctl']))),
    # RHEL7 with only uname provided
    (7, Case(None, None, None, None),
        (False, set())),
    # RHEL6 loaded not disabled
    (6, Case(None, LSMOD_LOADED, MODPROBE_NOT_DISABLED,
             SYSCTL_NOT_DISABLED), (False, set())),
    # RHEL6 not loaded but not disabled
    (6, Case(None, LSMOD_NOT_LOADED, MODPROBE_NOT_DISABLED,
             SYSCTL_NOT_DISABLED), (False, set())),
    # RHEL6 fake installed but loaded
    (6, Case(None, LSMOD_LOADED, MODPROBE_FAKE, SYSCTL_NOT_DISABLED),
        (False, set())),
    # RHEL6 not loaded, fake install commented
    (6, Case(None, LSMOD_NOT_LOADED, MODPROBE_FAKE_COMMENTED,
             SYSCTL_NOT_DISABLED), (False, set())),
    # RHEL6 loaded but disabled via modprobe
    (6, Case(None, LSMOD_LOADED, MODPROBE_DISABLED, SYSCTL_NOT_DISABLED),
        (True, set(['modprobe_disable']))),
    # RHEL6 not loaded, disabled via modprobe
    (6, Case(None, LSMOD_NOT_LOADED, MODPROBE_DISABLED,
             SYSCTL_NOT_DISABLED), (True, set(['modprobe_disable']))),
    # RHEL6 not loaded, disabled via fake install
    (6, Case(None, LSMOD_NOT_LOADED, MODPROBE_FAKE, SYSCTL_NOT_DISABLED),
        (True, set(['fake_install']))),
    # RHEL6 loaded but disabled by sysctl
    (6, Case(None, LSMOD_LOADED, MODPROBE_NOT_DISABLED, SYSCTL_DISABLED),
        (True, set(['sysctl']))),
    # RHEL6 not loaded, disabled by sysctl
    (6, Case(None, LSMOD_NOT_LOADED, MODPROBE_NOT_DISABLED,
             SYSCTL_DISABLED), (True, set(['sysctl']))),
    # RHEL6 disabled by modprobe and sysctl
    (6, Case(None, LSMOD_NOT_LOADED, MODPROBE_DISABLED, SYSCTL_DISABLED),
        (True, set(['sysctl', 'modprobe_disable']))),
    # RHEL6 with lsmod but no modprobe
    (6, Case(None, LSMOD_LOADED, None, None),
        (False, set())),
    # RHEL6 with modprobe but no lsmod
    (6, Case(None, None, MODPROBE_DISABLED, None),
        (True, set(['modprobe_disable']))),
    # RHEL6 with fake install but no lsmod (insufficient data)
    (6, Case(None, None, MODPROBE_FAKE, None),
        (False, set())),
    # RHEL6 with command line only
    (6, Case(CMDLINE_RHEL6_DISABLED, None, None, None),
        (True, set(['cmdline']))),
]


def test_integration():
    for rhel, case, result in CASES:
        context = dict()
        context[Uname] = Uname(context_wrap(
                               UNAME_RHEL7 if rhel == 7 else UNAME_RHEL6))

        if case.modprobe is not None:
            context[ModProbe] = ModProbe(context_wrap(case.modprobe,
                                         path='/etc/modprobe.d/ipv6.conf'))
        if case.lsmod is not None:
            context[LsMod] = LsMod(context_wrap(case.lsmod))

        if case.cmdline is not None:
            context[CmdLine] = CmdLine(context_wrap(case.cmdline))

        if case.sysctl is not None:
            context[Sysctl] = Sysctl(context_wrap(case.sysctl))

        un = context.get(Uname)
        mp = context.get(ModProbe)
        lsm = context.get(LsMod)
        cl = context.get(CmdLine)
        sct = context.get(Sysctl)

        ipv6 = IPv6(un, mp, lsm, cl, sct)
        assert ipv6.disabled() == result[0]
        assert ipv6.disabled_by() == result[1]
