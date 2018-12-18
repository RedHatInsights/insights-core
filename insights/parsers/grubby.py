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
from insights.parsers import SkipException, ParseException
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
            raise SkipException('Invalid output: {0}', content)


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
            raise SkipException('Invalid output: {0}', content)


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
        SkipException: When output is empty
        ParseException: When output is invalid

    Attributes:
        kernel_entries(list): List of dictionary for each kernel entry.
        boot(str): The `boot` value for RHEL6 only. None for RHEL7
    """
    def parse_content(self, content):

        def _add_entry(data, entry):
            # Skip the last empty index for RHEL7
            if entry and not(len(entry) == 1 and 'index' in entry):
                if (not entry.get('index') or
                        not entry.get('kernel') or
                        not entry.get('args') or
                        not entry.get('root') or
                        not entry.get('initrd')):
                    raise ParseException('Miss key parameters in {0}', entry)
                data.update({entry['kernel']: entry})

        if not content:
            raise SkipException('Empty output')

        # For RHEL6, the first line is 'boot=xxxx'
        self.boot = content.pop(0).split('=', 1)[-1].strip() if content[0].startswith('boot=') else None
        # For RHEL7, the last line is 'non linux entry'
        if content[-1] == 'non linux entry':
            del content[-1]

        self.data = self.kernel_entries = {}
        entry = {}
        for line in content:
            if '=' not in line:
                raise ParseException('Invalid line: {0}', line)
            line = line.strip()
            k, v = [v.strip() for v in line.split('=', 1)]
            if k == 'index':
                _add_entry(self.data, entry)
                entry = {}
            entry[k] = v.strip('"\'')
        _add_entry(self.data, entry)

    def __getitem__(self, item):
        """
        Returns (dict): The required kernel entry dictionary.
            - When ``item`` is string, returns the kernel entry with ``kernel`` is ``item``
            - When ``item`` is int, returns the kernel entry with ``index`` is ``item``
        Raises:
            KeyError: When ``item`` is ``str`` but not such ``kernel`` or
                ``item`` is not ``str`` or ``int``
            IndexError: When ``item`` is ``int`` but no such ``index``
        """
        if isinstance(item, str):
            return self.data[item]
        if isinstance(item, int):
            if item < 0:
                raise IndexError('list index out of range: {0}'.format(item))
            return [v for e, v in self.data.items() if int(v['index']) == item][0]
        raise KeyError('KeyError: {0}'.format(item))
