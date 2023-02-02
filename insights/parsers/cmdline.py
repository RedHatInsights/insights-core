"""
CmdLine - file ``/proc/cmdline``
================================

This parser reads the ``/proc/cmdline`` file, which contains the arguments
given to the currently running kernel on boot.

"""
from insights.core import LegacyItemAccess, Parser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
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

    .. note::

        For special command line elements that include two "=", e.g.
        ``root=LABEL=/1``, "root" will be the key and "LABEL=/1" will be
        the value in the returned list.

        Some parameters (the returned keys) might be still effective
        even if there is '#' before it, e.g.: ``#rhgb``.  This should
        be checked by the rule.

    Sample input::

        BOOT_IMAGE=/vmlinuz-3.10.0-327.36.3.el7.x86_64 root=/dev/system_vg/Root ro rd.lvm.lv=system_vg/Root crashkernel=auto rd.lvm.lv=system_vg/Swap rhgb quiet LANG=en_GB.utf8

    Examples:
        >>> cmd['BOOT_IMAGE']
        ['/vmlinuz-3.10.0-327.36.3.el7.x86_64']
        >>> cmd['rd.lvm.lv']
        ['system_vg/Root', 'system_vg/Swap']
        >>> 'autofs' in cmd
        False
        >>> cmd.get('autofs') is None
        True
        >>> 'quiet' in cmd
        True
        >>> cmd.get('quiet')
        [True]
        >>> cmd['crashkernel']
        ['auto']

    Attributes:
        data (dict): Parsed booting arguments are stored in this dictionary
        cmdline (str): The RAW line of the ``/proc/cmdline``
    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent('Empty output')
        if len(content) != 1:
            raise ParseException('Invalid output: {0}', content)

        self.data = {}
        self.cmdline = content[0].strip()
        for el in self.cmdline.split():
            # Thanks to strip and split, el always contains something.
            key, value = el, True
            if "=" in el:
                key, value = el.split("=", 1)
            if key not in self.data:
                self.data[key] = []
            self.data[key].append(value)
