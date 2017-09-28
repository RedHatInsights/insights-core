"""
UserNamespaces - Check whether user namespaces are enabled
==========================================================

This combiner reports whether user namespaces are enabled for the running
system per the kernel command line, and if grub info is available, for which
boot configurations they're enabled.

The user namespaces feature was introduced in kernel version 3.8, first shipped
in RHEL 7.x. It is built into the kernel, but requires an option to enable:

``user_namespaces.enable=1``

There are a few checks which are presently left to callers:
    * ``enabled()`` doesn't check whether the kernel supports user namespaces, only that the command line argument to enable them is present.

    * There is currently no attempt to relate the current kernel to a grub entry, which may be useful to know, if e.g. grub configuration has been changed, but the system needs a reboot.

"""

from ..core.plugins import combiner
from ..parsers.cmdline import CmdLine
from ..parsers.grub_conf import Grub2Config


@combiner(CmdLine, optional=[Grub2Config])
class UserNamespaces(object):
    """A combiner which determines if user namespaces are enabled."""

    def __init__(self, cmdline, grub2):
        self.grub_cmdline = {}
        # Even if technically possible, it is extremely unlikely that Red Hat will ever
        # ship or support grub1 on a system with kernel > 3.8, so only grub2 config
        # is analyzed here.
        if grub2:
            self.grub_cmdline = grub2.boot_entries
        self.cmdline = getattr(cmdline, "data", {})

    def enabled(self):
        """Determine whether user namespaces are enabled or not.

        Returns:
            bool: True if user namespaces are enabled, false if they aren't,
            or if user namespaces aren't supported by this kernel.
        """
        return ('1' in self.cmdline.get('user_namespaces.enable', []) or
                '1' in self.cmdline.get('user-namespaces.enable', []))

    def enabled_configs(self):
        """Get boot configs for which user namespaces are enabled.

        Returns:
            list: A list of grub menu entries in which user namespaces are
            enabled.  An empty list if user namespaces aren't supported or grub
            data isn't available.
        """
        return [entry.name for entry in self.grub_cmdline
                    if 'user_namespaces.enable=1' in entry.cmdline or
                       'user-namespaces.enable=1' in entry.cmdline]
