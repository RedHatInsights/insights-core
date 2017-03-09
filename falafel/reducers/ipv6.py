"""
IPv6 - Check whether IPv6 is disabled
=====================================

This shared reducer reports whether the user has disabled IPv6 via one of the
many means available to do so. At present, only whether IPv6 is disabled on
the running system is reported; it provides no information regarding whether it
would continue to be after a reboot.

Per https://access.redhat.com/solutions/8709 , IPv6 may be disabled by

RHEL 7:
 * ``ipv6.disable=1`` Kernel command line argument
 * ``disable_ipv6`` option in ``sysctl``

RHEL 6:
 * ``option ipv6 disable=1`` in `modprobe.d`
 * ``install ipv6 /bin/true`` (fake install) in `modprobe.d`
 * ``disable_ipv6`` option in ``sysctl``

While they aren't tested explicitly, there are some means by which you can
attempt to disable IPv6 that are ineffective, such as setting
``blacklist ipv6`` in `modprobe.d`; those methods will yield no result from
this reducer.

The only requirement of this reducer is ``Uname``, but accurate detection
relies on information from reducers marked optional. If, for example, it's run
against a RHEL6 system without information from ``ModProbe``, it will miss any
of those disabling options and possibly return a false negative. For that
reason, this reducer shouldn't be relied on to state definitively that IPv6 is
enabled or disabled.

Examples:
    >>> from falafel.tests import context_wrap
    >>> from falafel.mappers.uname import Uname
    >>> from falafel.mappers.sysctl import Sysctl
    >>> from falafel.reducers.ipv6 import IPv6
    >>> my_uname = '''
    ...  Linux localhost.localdomain 3.10.0-514.10.2.el7.x86_64 #1 SMP Mon Feb 20 02:37:52 EST 2017 x86_64 x86_64 x86_64 GNU/Linux
    ... '''.strip()
    >>> my_sysctl = '''
    ... net.ipv6.conf.all.autoconf = 1
    ... net.ipv6.conf.all.dad_transmits = 1
    ... net.ipv6.conf.all.disable_ipv6 = 0
    ... net.ipv6.conf.all.force_mld_version = 0
    ... net.ipv6.conf.all.force_tllao = 0
    ... net.ipv6.conf.all.forwarding = 0
    ... '''.strip()
    >>> shared = {Uname: Uname(context_wrap(my_uname)), Sysctl: Sysctl(context_wrap(my_sysctl))}
    >>> my_ipv6 = IPv6({},shared)
    >>> my_ipv6.disabled()
    set([])
    >>> my_sysctl = '''
    ... net.ipv6.conf.all.autoconf = 1
    ... net.ipv6.conf.all.dad_transmits = 1
    ... net.ipv6.conf.all.disable_ipv6 = 1
    ... net.ipv6.conf.all.force_mld_version = 0
    ... net.ipv6.conf.all.force_tllao = 0
    ... net.ipv6.conf.all.forwarding = 0
    ... '''.strip()
    >>> shared[Sysctl] = Sysctl(context_wrap(my_sysctl))
    >>> my_ipv6 = IPv6({},shared)
    >>> my_ipv6.disabled()
    set(['sysctl'])

"""

from ..core.plugins import reducer
from ..mappers.modprobe import ModProbe
from ..mappers.lsmod import LsMod
from ..mappers.cmdline import CmdLine
from ..mappers.sysctl import Sysctl
from ..mappers.uname import Uname


@reducer(requires=[Uname], optional=[ModProbe, LsMod, CmdLine, Sysctl],
         shared=True)
class IPv6(object):
    """A shared reducer which detects disabled IPv6 networking."""

    def __init__(self, local, shared):
        self.disabled_by = set()
        self.uname = shared[Uname]
        self.modprobe = shared.get(ModProbe)
        self.lsmod = shared.get(LsMod)
        self.cmdline = shared.get(CmdLine)
        self.sysctl = shared.get(Sysctl)

        self._check_ipv6()

    def _check_ipv6(self):
        # EL7 has IPv6 built in, it has to be disabled via the linux cmdline
        if self.uname.rhel_release[0] == '7':
            if self.cmdline:
                if self.cmdline.data.get('ipv6.disable') == ['1']:
                    self.disabled_by.add('cmdline')

        # EL6 requires lsmod and modprobe to state definitively whether the
        # module is disabled or not
        if (self.uname.rhel_release[0] == '6' and
                hasattr(self.lsmod, 'data') and
                hasattr(self.modprobe, 'data')):
            # Even if the module is loaded, IPv6 networking may still be
            # disabled.
            if 'ipv6' in self.lsmod:
                if self.modprobe.data.get('options',
                                          {}).get('ipv6') == ['disable=1']:
                    self.disabled_by.add('modprobe_disable')

            # Even if the module isn't loaded, it might be, unless it's fake
            # installed, and it may still be disabled
            else:
                if self.modprobe.data.get('install',
                                          {}).get('ipv6') == ['/bin/true']:
                    self.disabled_by.add('fake_install')
                if self.modprobe.data.get('options',
                                          {}).get('ipv6') == ['disable=1']:
                    self.disabled_by.add('modprobe_disable')

        # IPv6 can also be disabled via sysctl. Though it may be disabled on a
        # per-interface basis, this reducer only reports if it's turned off
        # for the whole system.
        # Additionally, the disable_ipv6 option in the RHEL6 kernel module sets
        # disable_ipv6 on each adapter, but for some reason not "all", which
        # may be missed by this reducer.
        # Also not reported is whether it's disabled in sysctl.conf and so
        # would persist between reboots.
        if self.sysctl:
            if '1' in self.sysctl.data.get('net.ipv6.conf.all.disable_ipv6',
                                           ()):
                self.disabled_by.add('sysctl')

    def disabled(self):
        """Determine whether IPv6 has been disabled on this system.

        Returns:
            set: Empty set if IPv6 has not been disabled, otherwise the
            configuration locations where it has been disabled.
        """
        return self.disabled_by
