"""
CmdLine - file ``/proc/cmdline``
================================

This reads the ``/proc/cmdline`` file, which contains the arguments given to
the currently running kernel on boot.

Sample input::

    BOOT_IMAGE=/vmlinuz-3.10.0-327.36.3.el7.x86_64 root=/dev/system_vg/Root ro rd.lvm.lv=system_vg/Root crashkernel=auto rd.lvm.lv=system_vg/Swap rhgb quiet LANG=en_GB.utf8

Examples:

    >>> cmd = shared[CmdLine]
    >>> cmd.data['BOOT_IMAGE']
    ['/vmlinuz-3.10.0-327.36.3.el7.x86_64']
    >>> cmd.data['rd.lvm.lv']
    ['system_vg/Root', 'system_vg/Swap']
    >>> 'crashkernel' in cmd.data
    True
    >>> 'autofs' in cmd.data
    False
    >>> 'quiet' in cmd.data
    True
    >>> cmd.data['quiet']
    None

"""

from .. import Parser, parser, LegacyItemAccess


@parser('cmdline')
class CmdLine(LegacyItemAccess, Parser):
    """
    A parser class for parsing the Linux kernel command line as given in
    ``/proc/cmdline``.
    """

    def parse_content(self, content):
        """
        If an element doesn't contain "=", set itself as key and the
        corresponding value to None.

        If an element contains "=", the corresponding values are stored in a
        list.

        For special command line elements that include two "=", e.g.
        ``root=LABEL=/1``, "root" will be the key and "LABEL=/1" will be the
        value in the returned list.

        Note: Some parameters (the returned keys) might be still effective
        even if there is '#' before it, e.g.: ``#rhgb``.  This should
        be checked by the rule.
        """

        cmdline_properties = {}
        line = content[0]
        for el in line.strip().split(None):
            # Thanks to strip and split, el always contains something.
            if "=" not in el:
                cmdline_properties[el] = None
            else:
                (key, value) = el.split("=", 1)
                cmdline_properties.setdefault(key, []).append(value)
        self.data = cmdline_properties
