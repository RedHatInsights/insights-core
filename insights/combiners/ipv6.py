"""
IPv6 - Check whether IPv6 is disabled
=====================================

This combiner reports whether the user has disabled IPv6 via one of the
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
this combiner.

The only requirement of this combiner is ``Uname``, but accurate detection
relies on information from combiners marked optional. If, for example, it's run
against a RHEL6 system without information from ``ModProbe``, it will miss any
of those disabling options and possibly return a false negative. For that
reason, this combiner shouldn't be relied on to state definitively that IPv6 is
enabled or disabled.

Examples:
    >>> from insights.tests import context_wrap
    >>> from insights.parsers.uname import Uname
    >>> from insights.parsers.sysctl import Sysctl
    >>> from insights.combiners.ipv6 import IPv6
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
    False
    >>> my_ipv6.disabled_by()
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
    True
    >>> my_ipv6.disabled_by()
    set(['sysctl'])

"""

from ..core.plugins import combiner
from ..parsers.modprobe import ModProbe
from ..parsers.lsmod import LsMod
from ..parsers.cmdline import CmdLine
from ..parsers.sysctl import Sysctl
from ..parsers.uname import Uname


RHEL_UNSUPPORTED_VERSION = 9999


@combiner(Uname, optional=[ModProbe, LsMod, CmdLine, Sysctl])
class IPv6(object):
    """A combiner which detects disabled IPv6 networking."""

    def __init__(self, uname, mod_probe, lsmod, cmdline, sysctl):
        self.disablers = set()

        if uname.rhel_release[0] == '7':
            self.rhelver = 7
        elif uname.rhel_release[0] == '6':
            self.rhelver = 6
        elif uname.rhel_release[0] == '5':
            self.rhelver = 5
        else:
            self.rhelver = RHEL_UNSUPPORTED_VERSION

        # ModProbe may be either a list or a ModProbe object, or
        # None if it wasn't provided. Make it safe to iterate over.
        self.modprobe = mod_probe or []
        if isinstance(self.modprobe, ModProbe):
            self.modprobe = [self.modprobe]

        # A dict of loaded modules if lsmod data was provided, or None,
        # because it's worth distinguishing whether the data was provided.
        self.lsmod = getattr(lsmod, 'data', None)

        # Nothing depends on command line data being provided, so default
        # to an empty dict
        self.cmdline = getattr(cmdline, 'data', {})

        # Likewise for sysctl data
        self.sysctl = getattr(sysctl, 'data', {})

        self._check_ipv6()

    def _check_ipv6(self):
        # Whether IPv6 is provided as a module or built in, it can be disabled
        # with the kernel command line
        if self.cmdline.get('ipv6.disable') == ['1']:
            self.disablers.add('cmdline')

        # IPv6 can also be disabled via sysctl. Though it may be disabled on a
        # per-interface basis, this combiner only reports if it's turned off
        # for the whole system.
        # Additionally, the disable_ipv6 option in the IPv6 kernel module sets
        # disable_ipv6 on each adapter, but for some reason not "all", which
        # may be missed by this combiner.
        # Also not reported is whether it's disabled in sysctl.conf and so
        # would persist between reboots.
        if self.sysctl.get('net.ipv6.conf.all.disable_ipv6') == '1':
            self.disablers.add('sysctl')

        # Pre-EL7 requires modprobe to state definitively whether the module
        # is disabled or not
        if (self.rhelver < 7 and len(self.modprobe) > 0):
            # Iterate over one or more sources of modprobe data
            for it in self.modprobe:
                # Whether or not the module is loaded, it may be disabled by
                # module options
                if it.get('options', {}).get('ipv6') == ['disable=1']:
                    self.disablers.add('modprobe_disable')

                # If the module is not currently loaded, a fake install will
                # prevent it from loading
                if self.lsmod is not None and 'ipv6' not in self.lsmod:
                    if it.get('install', {}).get('ipv6') == ['/bin/true']:
                        self.disablers.add('fake_install')

    def disabled(self):
        """Determine whether IPv6 has been disabled on this system.

        Returns:
            bool: True if a configuration that disables IPv6 was found.
        """
        return self.disablers != set([])

    def disabled_by(self):
        """Get the means by which IPv6 was disabled on this system.

        Returns:
            set: Zero or more of ``cmdline``, ``modprobe_disable``,
            ``fake_install``, or ``sysctl``, depending on which methods to
            disable IPv6 have been found.
        """
        return self.disablers
