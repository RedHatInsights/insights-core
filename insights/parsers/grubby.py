"""
Grubby - command ``/usr/sbin/grubby``
=====================================

This is a collection of parsers that all deal with the command ``grubby``.
Parsers included in this module are:

GrubbyDefaultIndex - command ``grubby --default-index``
-------------------------------------------------------

GrubbyInfoAll - command ``grubby --info=ALL``
---------------------------------------------
"""

from insights.core import CommandParser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.parsers import parse_cmdline_args
from insights.specs import Specs


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
        error_lines (list): the error messages from the grubby command
    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent('Empty output')

        self.error_lines = []
        default_index_line = content[0]
        if len(content) != 1:
            default_index_line = content[-1]
            self.error_lines = content[:-1]

        if not default_index_line.strip().isdigit():
            raise ParseException('Invalid output: {0}'.format(content))

        self.default_index = int(default_index_line.strip())


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
                    raise ParseException('Invalid index value: {0}'.format(_line))
            elif k == "args":
                entry_data["raw_args"] = v
                entry_data[k] = parse_cmdline_args(v)
            else:
                entry_data[k] = v

        if entry_data and "index" in entry_data and len(entry_data) > 1:
            self.boot_entries[entry_data["index"]] = entry_data

        if not self.boot_entries:
            raise SkipComponent("No valid entry parsed")
