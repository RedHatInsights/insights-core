"""
CmdLine - file ``/proc/cmdline``
================================

This parser reads the ``/proc/cmdline`` file, which contains the arguments
given to the currently running kernel on boot.

Sample input::

    BOOT_IMAGE=/vmlinuz-3.10.0-327.36.3.el7.x86_64 root=/dev/system_vg/Root ro rd.lvm.lv=system_vg/Root crashkernel=auto rd.lvm.lv=system_vg/Swap rhgb quiet LANG=en_GB.utf8

Examples:

    >>> cmd = shared[CmdLine]
    >>> cmd['BOOT_IMAGE']
    ['/vmlinuz-3.10.0-327.36.3.el7.x86_64']
    >>> cmd['rd.lvm.lv']
    ['system_vg/Root', 'system_vg/Swap']
    >>> 'crashkernel' in cmd
    True
    >>> 'autofs' in cmd
    False
    >>> 'quiet' in cmd
    True
    >>> cmd['quiet']
    None

"""

from .. import Parser, parser, LegacyItemAccess


@parser('cmdline')
class CmdLine(LegacyItemAccess, Parser):
    """
    A parser class for parsing the Linux kernel command line as given in
    ``/proc/cmdline``.

    Parsing Logic::

        If an element doesn't contain "=", set itself as key and the
        corresponding value to None.

        If an element contains "=", the corresponding values are stored in a
        list.

        Note:
            For special command line elements that include two "=", e.g.
            ``root=LABEL=/1``, "root" will be the key and "LABEL=/1" will be
            the value in the returned list.

            Some parameters (the returned keys) might be still effective
            even if there is '#' before it, e.g.: ``#rhgb``.  This should
            be checked by the rule.
    """

    def parse_content(self, content):
        cmdline_properties = {}
        for el in content[0].strip().split(None):
            # Thanks to strip and split, el always contains something.
            key, value = el, None
            if "=" in el:
                key, value = el.split("=", 1)

            if key not in cmdline_properties:
                cmdline_properties[key] = value if value is None else [value]
            else:
                if not isinstance(cmdline_properties[key], list):
                    cmdline_properties[key] = [cmdline_properties[key]]
                cmdline_properties[key].append(value)
        self.data = cmdline_properties
