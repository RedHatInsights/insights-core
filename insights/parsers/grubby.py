"""
Grubby - command ``/usr/sbin/grubby``
=====================================

This is a collection of parsers that all deal with the command ``grubby``.
Parsers included in this module are:

GrubbyDefaultIndex - command ``grubby --default-index``
-------------------------------------------------------

GrubbyDefaultKernel - command ``grubby --default-kernel``
---------------------------------------------------------

GrubbyInfoAll - command ``grubby --info=ALL``
---------------------------------------------
"""

from insights.core import CommandParser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs
from insights.util import deprecated


@parser(Specs.grubby_default_index)
class GrubbyDefaultIndex(CommandParser):
    """
    This parser parses the output of command ``grubby --default-index``.

    The typical output of this command is::

        0

    Examples:
        >>> grubby_default_index.default_index
        0

    Raises:
        SkipComponent: When output is empty
        ParseException: When output is invalid

    Attributes:
        default_index (int): the numeric index of the current default boot entry, count from 0
    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent('Empty output')
        if len(content) != 1 or not content[0].isdigit():
            raise ParseException('Invalid output: {0}', content)
        self.default_index = int(content[0])


@parser(Specs.grubby_default_kernel)
class GrubbyDefaultKernel(CommandParser):
    """
    .. warning::
        This class is deprecated and will be removed from 3.7.0.
        Please use the :class:`insights.combiners.grubby.Grubby` instead.

    This parser parses the output of command ``grubby --default-kernel``.

    The typical output of this command is::

        /boot/vmlinuz-2.6.32-573.el6.x86_64

    Examples:

        >>> grubby_default_kernel.default_kernel
        '/boot/vmlinuz-2.6.32-573.el6.x86_64'

    Raises:
        SkipComponent: When output is empty
        ParseException: When output is invalid

    Attributes:
        default_kernel(str): The default kernel name for next boot
    """

    def __init__(self, context):
        deprecated(
            GrubbyDefaultKernel,
            "Please use the :class:`insights.combiners.grubby.Grubby` instead.",
            "3.7.0",
        )
        super(GrubbyDefaultKernel, self).__init__(context)

    def parse_content(self, content):
        if not content:
            raise SkipComponent('Empty output')

        # Skip the error lines to find the real default-kernel line.
        # Typically, the default-kernel line is the last line in content.
        default_kernel_str = None

        if len(content) == 1:
            default_kernel_str = content[0].strip()
        else:
            for idx in range(len(content) - 1, -1, -1):
                line = content[idx]
                if line.startswith('/boot/') and '/boot/vmlinuz-' in line:
                    if not default_kernel_str:
                        default_kernel_str = line.strip()
                    else:
                        raise ParseException('Invalid output: duplicate kernel lines: {0}', content)

        if not default_kernel_str:
            raise ParseException('Invalid output: no kernel line: {0}', content)
        if len(default_kernel_str.split()) > 1:
            raise ParseException('Invalid output: unparsable kernel line: {0}', content)

        self.default_kernel = default_kernel_str


@parser(Specs.grubby_info_all)
class GrubbyInfoAll(CommandParser):
    """
    This parser parses the output of command ``grubby --info=ALL``.

    Attributes:
        boot_entries (dict): All boot entries indexed by the entry "index"
        unparsed_lines (list): All the unparsable lines

    The typical output of this command is::

        index=0
        kernel="/boot/vmlinuz-5.14.0-162.6.1.el9_1.x86_64"
        args="ro crashkernel=1G-4G:192M,4G-64G:256M,64G-:512M resume=/dev/mapper/rhel-swap rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet retbleed=stuff"
        root="/dev/mapper/rhel-root"
        initrd="/boot/initramfs-5.14.0-162.6.1.el9_1.x86_64.img"
        title="Red Hat Enterprise Linux (5.14.0-162.6.1.el9_1.x86_64) 9.1 (Plow)"
        id="4d684a4a6166439a867e701ded4f7e10-5.14.0-162.6.1.el9_1.x86_64"
        index=1
        kernel="/boot/vmlinuz-5.14.0-70.13.1.el9_0.x86_64"
        args="ro crashkernel=1G-4G:192M,4G-64G:256M,64G-:512M resume=/dev/mapper/rhel-swap rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet retbleed=stuff"
        root="/dev/mapper/rhel-root"
        initrd="/boot/initramfs-5.14.0-70.13.1.el9_0.x86_64.img"
        title="Red Hat Enterprise Linux (5.14.0-70.13.1.el9_0.x86_64) 9.0 (Plow)"
        id="4d684a4a6166439a867e701ded4f7e10-5.14.0-70.13.1.el9_0.x86_64"

    Examples:

        >>> len(grubby_info_all.boot_entries)
        2
        >>> grubby_info_all.boot_entries[0]["kernel"]
        '/boot/vmlinuz-5.14.0-162.6.1.el9_1.x86_64'
        >>> grubby_info_all.boot_entries[1].get("args").get("rd.lvm.lv")
        ['rhel/root', 'rhel/swap']

    Raises:
        SkipComponent: When output is empty
        ParseException: When output is invalid
    """

    def parse_content(self, content):

        def _parse_args(args):
            parsed_args = dict()
            for el in args.split():
                key, value = el, True
                if "=" in el:
                    key, value = el.split("=", 1)
                if key not in parsed_args:
                    parsed_args[key] = []
                parsed_args[key].append(value)
            return parsed_args

        if not content:
            raise SkipComponent("Empty output")

        self.boot_entries = {}
        self.unparsed_lines = []

        entry_data = {}
        for _line in content:
            line = _line.strip()

            if not line:
                continue
            if "=" not in line:
                self.unparsed_lines.append(_line)
                continue

            k, v = line.split("=", 1)
            v = v.strip("'\"")
            if k == "index":
                if v.isdigit():
                    if entry_data and "index" in entry_data and len(entry_data) > 1:
                        self.boot_entries[entry_data["index"]] = entry_data
                    entry_data = {k: int(v)}
                else:
                    raise ParseException('Invalid index value: {0}', _line)
            elif k == "args":
                entry_data[k] = _parse_args(v)
            else:
                entry_data[k] = v

        if entry_data and "index" in entry_data and len(entry_data) > 1:
            self.boot_entries[entry_data["index"]] = entry_data

        if not self.boot_entries:
            raise SkipComponent("No valid entry parsed")
