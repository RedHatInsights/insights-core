"""
grubby - command ``/usr/sbin/grubby``
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

from insights.specs import Specs
from insights.parsers import SkipException, split_kv_pairs
from insights import CommandParser, LegacyItemAccess
from insights import parser


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
        SkipException: When output is invalid or empty

    Attributes:
        default_index (int): the numeric index of the current default boot entry, count from 0
    """
    def parse_content(self, content):
        if content and len(content) == 1 and content[0].isdigit():
            self.default_index = int(content[0])
        else:
            raise SkipException('Invalid output: {}', content)


@parser(Specs.grubby_default_kernel)
class GrubbyDefaultKernel(CommandParser):
    """
    This parser parses the output of command ``grubby --default-kernel``.

    The typical output of this command is::

        /boot/vmlinuz-2.6.32-573.el6.x86_64

    Examples:

        >>> grubby_default_kernel.default_kernel
        '/boot/vmlinuz-2.6.32-573.el6.x86_64'

    Raises:
        SkipException: When output is invalid or empty

    Attributes:
        default_kernel(str): The default kernel name for next boot
    """
    def parse_content(self, content):
        if content and len(content) == 1:
            self.default_kernel = content[0].strip()
        else:
            raise SkipException('Invalid output: {}', content)


@parser(Specs.grubby_info_all)
class GrubbyInfoALL(CommandParser, LegacyItemAccess):
    """
    This parser parses the output of command ``grubby --info=ALL``.

    The typical output of this command is::

        boot=/dev/vda
        index=0
        kernel=/vmlinuz-2.6.32-754.9.1.el6.x86_64
        args="ro rd_NO_LUKS rd_NO_LVM LANG=en_US.UTF-8 rd_NO_MD SYSFONT=latarcyrheb-sun16 crashkernel=auto  KEYBOARDTYPE=pc KEYTABLE=us rd_NO_DM rhgb quiet"
        root=UUID=1b46779e-4fae-442d-a2ac-dd6d8563ff3e
        initrd=/boot/initramfs-2.6.32-754.9.1.el6.x86_64.img
        index=1
        kernel=/vmlinuz-2.6.32-573.el6.x86_64
        args="ro rd_NO_LUKS rd_NO_LVM LANG=en_US.UTF-8 rd_NO_MD SYSFONT=latarcyrheb-sun16 crashkernel=auto  KEYBOARDTYPE=pc KEYTABLE=us rd_NO_DM rhgb quiet"
        root=UUID=1b46779e-4fae-442d-a2ac-dd6d8563ff3e
        initrd=/boot/initramfs-2.6.32-573.el6.x86_64.img

    Examples:

        >>> len(grubby_info_all.kernel_entries)
        2
        >>> grubby_info_all[0]['kernel']
        '/vmlinuz-2.6.32-754.9.1.el6.x86_64'
        >>> '/vmlinuz-2.6.32-754.9.1.el6.x86_64' in grubby_info_all
        True
        >>> grubby_info_all.get('/vmlinuz-2.6.32-754.9.1.el6.x86_64')['root']
        'UUID=1b46779e-4fae-442d-a2ac-dd6d8563ff3e'
        >>> grubby_info_all[0] == grubby_info_all['/vmlinuz-2.6.32-754.9.1.el6.x86_64']
        True

    Raises:
        SkipException: When output is invalid or empty

    Attributes:
        kernel_entries(list): List of dictionary for each kernel entry.
        boot(str): The `boot` value for RHEL6 only. None for RHEL7
    """
    def parse_content(self, content):
        if not content or len(content) <= 5:
            raise SkipException('Invalid output: {}', content)
        self.data = self.kernel_entries = {}
        self.boot = None
        idxs = [
            i
            for i, l in enumerate(content)
            if l.startswith(('index=', 'boot='))
        ]
        # For RHEL6, the first line is 'boot=xxxx'
        if idxs and content[idxs[0]].startswith('boot='):
            self.boot = content[idxs.pop(0)].split('=', 1)[-1].strip()
        for i, idx in enumerate(idxs):
            start = idx
            end = idxs[i + 1] if i < len(idxs) - 1 else -1
            entry = split_kv_pairs(content[start:end])
            self.data.update({entry['kernel']: entry}) if entry and 'kernel' in entry else None

    def __getitem__(self, item):
        """
        Returns (dict): The required kernel entry dictionary.
            - When ``item`` is string, returns the kernel entry with ``kernel`` is ``item``
            - When ``item`` is int, returns the kernel entry with ``index`` is ``item``
        Raises:
            KeyError: When ``item`` is a ``str`` but not such ``kernel``
            IndexError: When ``item`` is a ``int`` but no such ``index``
        """
        if isinstance(item, str):
            return self.data[item]
        if isinstance(item, int):
            if item < 0:
                raise IndexError('list index out of range: {}'.format(item))
            return [v for e, v in self.data.items() if int(v['index']) == item][0]
