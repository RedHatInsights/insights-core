from ..ipv6 import IPv6
from ...mappers.modprobe import ModProbe
from ...mappers.lsmod import LsMod
from ...mappers.cmdline import CmdLine
from ...mappers.sysctl import Sysctl
from ...mappers.uname import Uname
from ...tests import context_wrap

from collections import namedtuple

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
        (7, Case(CMDLINE_NOT_DISABLED, "", "", SYSCTL_NOT_DISABLED),
            set()),
        # RHEL7 disabled via cmdline
        (7, Case(CMDLINE_DISABLED, "", "", SYSCTL_NOT_DISABLED),
            set(['cmdline'])),
        # RHEL7 disabled via sysctl
        (7, Case(CMDLINE_NOT_DISABLED, "", "", SYSCTL_DISABLED),
            set(['sysctl'])),
        # RHEL7 disabled by both cmdline and sysctl
        (7, Case(CMDLINE_DISABLED, "", "", SYSCTL_DISABLED),
            set(['cmdline', 'sysctl'])),
        # RHEL6 loaded not disabled
        (6, Case("#", LSMOD_LOADED, MODPROBE_NOT_DISABLED,
                 SYSCTL_NOT_DISABLED), set()),
        # RHEL6 not loaded but not disabled
        (6, Case("#", LSMOD_NOT_LOADED, MODPROBE_NOT_DISABLED,
                 SYSCTL_NOT_DISABLED), set()),
        # RHEL6 fake installed but loaded
        (6, Case("#", LSMOD_LOADED, MODPROBE_FAKE, SYSCTL_NOT_DISABLED),
            set()),
        # RHEL6 not loaded, fake install commented
        (6, Case("#", LSMOD_NOT_LOADED, MODPROBE_FAKE_COMMENTED,
                 SYSCTL_NOT_DISABLED), set()),
        # RHEL6 loaded but disabled via modprobe
        (6, Case("#", LSMOD_LOADED, MODPROBE_DISABLED, SYSCTL_NOT_DISABLED),
            set(['modprobe_disable'])),
        # RHEL6 not loaded, disabled via modprobe
        (6, Case("#", LSMOD_NOT_LOADED, MODPROBE_DISABLED,
                 SYSCTL_NOT_DISABLED), set(['modprobe_disable'])),
        # RHEL6 not loaded, disabled via fake install
        (6, Case("#", LSMOD_NOT_LOADED, MODPROBE_FAKE, SYSCTL_NOT_DISABLED),
            set(['fake_install'])),
        # RHEL6 loaded but disabled by sysctl
        (6, Case("#", LSMOD_LOADED, MODPROBE_NOT_DISABLED, SYSCTL_DISABLED),
            set(['sysctl'])),
        # RHEL6 not loaded, disabled by sysctl
        (6, Case("#", LSMOD_NOT_LOADED, MODPROBE_NOT_DISABLED,
                 SYSCTL_DISABLED), set(['sysctl'])),
        # RHEL6 disabled by modprobe and sysctl
        (6, Case("#", LSMOD_NOT_LOADED, MODPROBE_DISABLED, SYSCTL_DISABLED),
            set(['sysctl', 'modprobe_disable'])),
        ]


def test_integration():
    for rhel, case, result in CASES:
        uname = Uname(context_wrap(UNAME_RHEL7 if rhel == 7 else UNAME_RHEL6))
        cmdline = CmdLine(context_wrap(case.cmdline))
        lsmod = LsMod(context_wrap(case.lsmod))
        modprobe = ModProbe(context_wrap(case.modprobe))
        sysctl = Sysctl(context_wrap(case.sysctl))
        ipv6 = IPv6({}, {CmdLine: cmdline, LsMod: lsmod, ModProbe: modprobe,
                         Sysctl: sysctl, Uname: uname})
        assert ipv6.disabled() == result
