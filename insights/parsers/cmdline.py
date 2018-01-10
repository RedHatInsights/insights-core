"""
CmdLine - File ``/proc/cmdline``
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
    >>> 'autofs' in cmd
    False
    >>> cmd.get('autofs')
    None
    >>> 'quiet' in cmd
    True
    >>> cmd.get('quiet')
    [True]
    >>> cmd['crashkernel']
    ['auto']

"""

from .. import Parser, parser, LegacyItemAccess
from insights.specs import Specs


@parser(Specs.cmdline)
class CmdLine(LegacyItemAccess, Parser):
    """
    A parser class for parsing the Linux kernel command line as given in
    ``/proc/cmdline``.

    Parsing Logic::

        Parses all elements in command line to a dict where the key is the
        element itself and the value is a list stores its corresponding values.

        If an element doesn't contain "=", set the corresponding value to `True`.

        If an element contains "=", set the corresponding value to the whole right
        value of the "=".

        Note:
            For special command line elements that include two "=", e.g.
            ``root=LABEL=/1``, "root" will be the key and "LABEL=/1" will be
            the value in the returned list.

            Some parameters (the returned keys) might be still effective
            even if there is '#' before it, e.g.: ``#rhgb``.  This should
            be checked by the rule.
    """

    def parse_content(self, content):
        self.data = {}
        for el in content[0].strip().split(None):
            # Thanks to strip and split, el always contains something.
            key, value = el, True
            if "=" in el:
                key, value = el.split("=", 1)
            if key not in self.data:
                self.data[key] = []
            self.data[key].append(value)
