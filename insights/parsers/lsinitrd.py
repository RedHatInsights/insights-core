"""
lsinitrd - command ``lsinitrd``
===============================

This module contains the following parsers:

Lsinitrd - command ``lsinitrd``
-------------------------------

LsinitrdKdumpImage - command ``lsinitrd initramfs-<kernel-version>kdump.img``
-----------------------------------------------------------------------------

LsinitrdLvmConf - command ``/bin/lsinitrd -f /etc/lvm/lvm.conf --kver {default_kernel_version}``
------------------------------------------------------------------------------------------------

"""

from insights import parser, CommandParser
from insights.core import ls_parser
from insights.specs import Specs
from insights.parsers import keyword_search
from insights.parsers.lvm import LvmConf


@parser(Specs.lsinitrd)
class Lsinitrd(CommandParser):
    """
    This parser parses the filtered output of command ``lsinitrd`` and provides
    the info of listed files.

    A parser for command "lsinitrd".

    Attributes:
        data (dict): The key is the filename, the value is a dict describe
            the file's info.
        unparsed_lines(list): List of strings for unparsed lines.

    As this lsinitrd spec is set to filterable, the structure of the output
    is broken. Hence, this parser will parse only filelisting like lines in
    output of 'lisinitrd', and also store all the unparsed lines.
    If the other parts of the output structure are required in the future,
    an enhancement may be performed then.

    Examples:
        >>> len(ls.data)
        5
        >>> assert ls.search(name__contains='kernel') == [
        ...    {'group': 'root', 'name': 'kernel/x86', 'links': 3, 'perms': 'rwxr-xr-x',
        ...     'raw_entry': 'drwxr-xr-x   3 root     root            0 Apr 20 15:58 kernel/x86',
        ...     'owner': 'root', 'date': 'Apr 20 15:58', 'type': 'd', 'dir': '', 'size': 0}
        ... ]
        >>> "udev-rules" in ls.unparsed_lines
        True
    """

    def parse_content(self, content):
        file_types = set(['s', 'd', 'p', 'l', '-', 'c', 'b'])
        perm = set(['-w-', 'rw-', '--x', '-wx', '---', 'rwx', 'r--', 'r-x'])
        entries = []
        _unparsed_lines = []

        for l in content:
            if l and len(l) > 10 and l[0] in file_types and l[1:4] in perm:
                entries.append(l)
            else:
                _unparsed_lines.append(l)
        self.unparsed_lines = _unparsed_lines

        d = ls_parser.parse(entries, '').get('')
        self.data = d.get('entries')

    def search(self, **kwargs):
        """
        Search the listed files for matching rows based on key-value pairs.

        This uses the :py:func:`insights.parsers.keyword_search` function for
        searching; see its documentation for usage details.  If no search
        parameters are given, no rows are returned.

        Returns:
            list: A list of dictionaries of files that match the given
            search criteria.

        Examples:
            >>> lsdev = ls.search(name__contains='dev')
            >>> len(lsdev)
            3
            >>> dev_console = {
            ...     'type': 'c', 'perms': 'rw-r--r--', 'links': 1, 'owner': 'root', 'group': 'root',
            ...     'major': 5, 'minor': 1, 'date': 'Apr 20 15:57', 'name': 'dev/console', 'dir': '',
            ...     'raw_entry': 'crw-r--r--   1 root     root       5,   1 Apr 20 15:57 dev/console'
            ... }
            >>> dev_console in lsdev
            True
            >>> 'dev/kmsg' in [l['name'] for l in lsdev]
            True
            >>> 'dev/null' in [l['name'] for l in lsdev]
            True

        """
        return keyword_search(self.data.values(), **kwargs)


@parser(Specs.lsinitrd_kdump_image)
class LsinitrdKdumpImage(Lsinitrd):
    """
    Parses output of ``lsinitrd initramfs-<kernel-version>kdump.img`` command.

    Sample ``lsinitrd initramfs-<kernel-version>kdump.img`` output::

        Image: initramfs-4.18.0-240.el8.x86_64kdump.img: 19M
        ========================================================================
        Version: dracut-049-95.git20200804.el8

        Arguments: --quiet --hostonly --hostonly-cmdline --hostonly-i18n --hostonly-mode 'strict' -o 'plymouth dash resume ifcfg earlykdump' --mount '/dev/mapper/rhel-root /sysroot xfs rw,relatime,seclabel,attr2,inode64,logbufs=8,logbsize=32k,noquota,nofail,x-systemd.before=initrd-fs.target' --no-hostonly-default-device -f

        dracut modules:
        bash
        systemd
        systemd-initrd
        i18n
        ========================================================================
        crw-r--r--   1 root     root       5,   1 Aug  4  2020 dev/console
        crw-r--r--   1 root     root       1,  11 Aug  4  2020 dev/kmsg
        crw-r--r--   1 root     root       1,   3 Aug  4  2020 dev/null
        crw-r--r--   1 root     root       1,   8 Aug  4  2020 dev/random
        crw-r--r--   1 root     root       1,   9 Aug  4  2020 dev/urandom
        drwxr-xr-x  14 root     root            0 Aug  4  2020 .
        lrwxrwxrwx   1 root     root            7 Aug  4  2020 bin -> usr/bin
        drwxr-xr-x   2 root     root            0 Aug  4  2020 dev
        ========================================================================

    Examples:
        >>> type(lsinitrd_kdump_image)
        <class 'insights.parsers.lsinitrd_kdump_image.LsinitrdKdumpImage'>
        >>> lsinitrd_kdump_image.search(name__contains='urandom')
        >>> len(result_list)
        1
        >>> result_list[0].get('raw_entry')
        'crw-r--r--   1 root     root       1,   9 Aug  4  2020 dev/urandom'
    """
    pass


@parser(Specs.lsinitrd_lvm_conf)
class LsinitrdLvmConf(LvmConf):
    """
    Parses the ``/dev/lvm/lvm.conf`` file get from the default initramfs.

    Sample Input::
        # volume_list = [ "vg1", "vg2/lvol1", "@tag1", "@*" ]
        volume_list = [ "vg2", "vg3/lvol3", "@tag2", "@*" ]

    Examples:
        >>> type(lsinitrd_lvm_conf)
        <class 'insights.parsers.lsinitrd.LsinitrdLvmConf'>
        >>> lsinitrd_lvm_conf.get("volume_list")
        [ "vg2", "vg3/lvol3", "@tag2", "@*" ]
    """
    pass
