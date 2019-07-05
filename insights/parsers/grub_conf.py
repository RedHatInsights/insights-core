"""
GRUB configuration files
========================

This parser reads the configuration of the GRand Unified Bootloader, versions
1 or 2.

This is currently a fairly simple parsing process.  Data read from the file
is put into roughly three categories:

* **configs**: lines read from the file that aren't boot options (i.e.
  excluding lines that go in the *title* and *menuentry* sections).  These
  are split into pairs on the first '=' sign.
* **title**: (GRUB v1 only) lines prefixed by the word 'title'.  All following
  lines up to the next title line are folded together.
* **menuentry**: (GRUB v2 only) lines prefixed by the word 'menuentry'.  All
  following lines up to the line starting with '}' are treated as part of one
  menu entry.

Each of these categories is (currently) stored as a simple list of tuples.

* For the list of **configs**, the tuples are (key, value) pairs based on
  the line, split on the first '=' character.  If nothing is found after the
  '=' character, then the value is ``None``.

* For the **title** list, there will be exactly two items in this list:

  * The first item will be a tuple of two items: 'title_name' and the
    title of the boot option.
  * The second item will be a tuple of two items: 'kernel' and the entire
    rest of the kernel boot line as if it had been given all on one line.

* For the **menuentry** list:

  * the first item will be a tuple of two items: 'menuentry_name' and the
    full text between 'menuentry' and '{'.
  * the rest of the items will be tuples of that line in the menu entry
    configuration, split on the first space.  If no space is found after the
    first word, the value will be ``None``.  So ``load_video`` will be stored
    as ``('load_video', None)`` and ``set root='hd0,msdos1'`` will be stored
    as ``('set', "root='hd0,msdos1'")``.

.. note::
    For GRUB version 2, all lines between the ``if`` and ``fi`` will be ignored
    due to we cannot analyze the result of the bash conditions.

There are several helper functions for dealing with the Intel IOMMU and for
extracting the kernel and initrd configurations available.

Parsers provided by this module are:

Grub1Config - file ``/boot/grub.conf``
--------------------------------------

Grub1EFIConfig - file ``/boot/efi/EFI/redhat/grub.conf``
--------------------------------------------------------

Grub2Config - file ``/boot/grub/grub2.cfg``
-------------------------------------------

Grub2EFIConfig - file ``/boot/efi/EFI/redhat/grub.cfg``
-------------------------------------------------------

Grub2Grubenv - file ``/boot/grub2/grubenv``
-------------------------------------------

Grub2EFIGrubenv - file ``/boot/efi/EFI/redhat/grubenv``
-------------------------------------------------------
"""

from insights import Parser
from insights import parser, get_active_lines, defaults
from insights.parsers import ParseException, SkipException
from insights.specs import Specs

IOMMU = "intel_iommu=on"
GRUB_KERNELS = 'grub_kernels'
GRUB_INITRDS = 'grub_initrds'


class BootEntry(dict):
    """
    An object representing an entry in the output of ``mount`` command.  Each
    entry contains below fixed attributes:

    Attributes:
        name (str): Name of the boot entry
        cmdline (str): Cmdline of the boot entry
    """
    def __init__(self, data={}):
        self.update(data)
        self.name = data.get('name', '')
        self.cmdline = data.get('cmdline', '')


class GrubConfig(Parser, dict):
    """
    Parser for configuration for both GRUB versions 1 and 2.
    """

    def parse_content(self, content):
        """
        Parse grub configuration file to create a dict with this structure::

            {
                "configs": [ (name, value), (name, value) ...],
                "title": [
                    [(name, name), (cmd, opt), (cmd, opt) ...],
                    [(title_name, another_name), ...]
                ],
                "menuentry": [
                    [(menuentry_name, its name), (cmd, opt), (cmd, opt) ...],
                    [(menuentry_name, another_name), ...]
                ],
            }

        """

        self.configs = []
        self.entries = self.title = self.menuentry = []
        entry = {}
        in_script = False
        if_idx = 0
        for line in get_active_lines(content):
            line = line.strip('{} \t')
            if line.startswith('if'):
                if_idx += 1
                in_script = True
                continue
            if line.startswith('fi'):
                if_idx -= 1
                in_script = True if if_idx else False
                continue
            if not in_script and line.startswith(('title ', 'menuentry')):
                self.entries.append(entry) if entry else None
                entry = {}
                if line.startswith('title '):
                    entry['title_name'] = line.split('title', 1)[1].strip()
                else:
                    entry['menuentry_name'] = line.split('menuentry', 1)[1].split('{', 1)[0].strip()
            elif not in_script and line:
                if entry:
                    sp = [i.strip() for i in line.split(None, 1)]
                    if sp[0] not in entry:
                        entry[sp[0]] = []
                    entry[sp[0]].append(sp[1] if len(sp) > 1 else '')
                else:
                    sep = '=' if '=' in line else None
                    sp = [i.strip() for i in line.split(sep, 1)]
                    self.configs.append((sp[0], sp[1] if len(sp) > 1 else ''))
        self.entries.append(entry) if entry else None

        self.update({'configs': self.configs}) if self.configs else None

        # while (True):
        #     try:

        #         if line is None:
        #             line = next(line_iter)

        #         if line.startswith('title '):
        #             last_line = _parse_title(line_iter, line, conf)
        #             line = last_line
        #         elif line.startswith('menuentry '):
        #             _parse_menu_entry(line_iter, line, conf)
        #             line = None
        #         else:
        #             conf["configs"].append(_parse_config(line))
        #             line = None

        #     except StopIteration:
        #         self.data = conf
        #         break

        self._boot_entries = []
        for entry in self.entries:
            s_entry = {}
            for k, v in entry.items():
                if k in ('menuentry_name', 'title_name'):
                    s_entry['name'] = v
                elif s_entry and k.startswith(('kernel', 'linux')):
                    s_entry['cmdline'] = v[0]
            self._boot_entries.append(BootEntry(s_entry))

    @property
    def boot_entries(self):
        """
        Get all boot entries in GRUB configuration.

        Returns:
            (list): A list of :class:`BootEntry` objects for each boot entry in below format:
                    - 'name': "Red Hat Enterprise Linux Server"
                    - 'cmdline': "kernel /vmlinuz-2.6.32-431.11.2.el6.x86_64 crashkernel=128M rhgb quiet"
        """

        return self._boot_entries

    @property
    def is_kdump_iommu_enabled(self):
        """
        Does any kernel have 'intel_iommu=on' set?

        Returns:
            (bool): ``True`` when 'intel_iommu=on' is set, otherwise returns ``False``
        """

        for line in self._boot_entries:
            if line.cmdline and IOMMU in line.cmdline:
                return True
        return False

    @property
    def kernel_initrds(self):
        """
        Get the `kernel` and `initrd` files referenced in GRUB configuration files

        Returns:
            (dict): Returns a dict of the `kernel` and `initrd` files referenced
                    in GRUB configuration files
        """

        kernels = []
        initrds = []
        name_values = []
        for k, v in self.configs:
            if (k.startswith(('module', 'kernel', 'linux', 'initrd'))):
                name_values.append((k, v))
        for entry in self.entries:
            for k, v in entry.items():
                if (k.startswith(('module', 'kernel', 'linux', 'initrd'))):
                    name_values.append((k, v))
        print('--')
        print(name_values)

        for name, value in name_values:
            v = None
            if isinstance(value, list):
                v = [i.split()[0].split('/')[-1] for i in value if i]
            elif value and isinstance(value, str):
                v = [value.split()[0].split('/')[-1]]
            if v:
                if name.startswith('module'):
                    kernels.extend([i for i in v if 'vmlinuz' in i])
                    initrds.extend([i for i in v if 'initrd' in i or 'initramfs' in i])
                elif (name.startswith(('kernel', 'linux'))):
                    if any('ipxe.lkrn' in i for i in v):
                        # Machine PXE boots the kernel, assume all is ok
                        return {}
                    elif 'xen.gz' not in v:
                        kernels.extend([i for i in v if 'xen.gz' not in i])
                elif name.startswith('initrd') or name.startswith('initrd16'):
                    initrds.extend(v)

        print({GRUB_KERNELS: kernels, GRUB_INITRDS: initrds})
        return {GRUB_KERNELS: kernels, GRUB_INITRDS: initrds}


@parser(Specs.grub_conf)
class Grub1Config(GrubConfig):
    """
    Parser for configuration for GRUB version 1.

    Examples:
        >>> grub1_content = '''
        ... default=0
        ... timeout=0
        ... splashimage=(hd0,0)/grub/splash.xpm.gz
        ... hiddenmenu
        ... title Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64)
        ...         kernel /vmlinuz-2.6.32-431.17.1.el6.x86_64 crashkernel=128M rhgb quiet
        ... title Red Hat Enterprise Linux Server (2.6.32-431.11.2.el6.x86_64)
        ...         kernel /vmlinuz-2.6.32-431.11.2.el6.x86_64 crashkernel=128M rhgb quiet
        ... '''.strip()

        >>> from insights.tests import context_wrap
        >>> shared = {Grub1Config: Grub1Config(context_wrap(grub1_content))}
        >>> config = shared[Grub1Config]
        >>> config['configs']
        [('default', '0'), ('timeout', '0'), ('splashimage', '(hd0,0)/grub/splash.xpm.gz'), ('hiddenmenu', None)]
        >>> config['title'][0]
        [('title_name', 'Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64)'), ('kernel', '/vmlinuz-2.6.32-431.17.1.el6.x86_64 crashkernel=128M rhgb quiet')]
        >>> config['title'][1][0][1]
        'Red Hat Enterprise Linux Server (2.6.32-431.11.2.el6.x86_64)'
        >>> config.boot_entries[1].name
        'Red Hat Enterprise Linux Server (2.6.32-431.11.2.el6.x86_64)'
        >>> config.boot_entries[1].cmdline
        "kernel /vmlinuz-2.6.32-431.11.2.el6.x86_64 crashkernel=128M rhgb quiet"
        >>> config.is_kdump_iommu_enabled
        False
        >>> config.kernel_initrds['grub_kernels'][0]
        'vmlinuz-2.6.32-431.17.1.el6.x86_64'
    """

    def __init__(self, *args, **kwargs):
        super(Grub1Config, self).__init__(*args, **kwargs)
        self._version = 1
        self._efi = False
        self.update({'title': self.title})

    def get_current_title(self):
        """
        Get the current default title from the ``default`` option in the
        main configuration. (GRUB v1 only)

        Returns:
            list: A list contains all settings of the default boot entry:
                  - [(title_name, name), (cmd, opt), (cmd, opt) ...]
        """
        # if no 'default' in grub.conf, set default to 0
        idx = '0'
        conf = self.configs
        for v in conf:
            if v[0] == 'default':
                idx = v[1]

        if idx.isdigit():
            idx = int(idx)
            title = self.title
            if len(title) > idx:
                return title[idx]

        return None


@parser(Specs.grub_efi_conf)
class Grub1EFIConfig(Grub1Config):
    """
    Parses grub v1 configuration for EFI-based systems
    Content of grub-efi.conf is the same as grub.conf
    """
    def __init__(self, *args, **kwargs):
        super(Grub1EFIConfig, self).__init__(*args, **kwargs)
        self._efi = True


@parser(Specs.grub2_cfg)
class Grub2Config(GrubConfig):
    """
    Parser for configuration for GRUB version 2.

    Examples:
        >>> grub2_content = '''
        ... ### BEGIN /etc/grub.d/00_header ###
        ... set pager=1
        ... /
        ... if [ -s $prefix/grubenv ]; then
        ...   load_env
        ... fi
        ... #[...]
        ... if [ x"${feature_menuentry_id}" = xy ]; then
        ...   menuentry_id_option="--id"
        ... else
        ...   menuentry_id_option=""
        ... fi
        ... #[...]
        ... ### BEGIN /etc/grub.d/10_linux ###
        ...     menuentry 'Red Hat Enterprise Linux Workstation (3.10.0-327.36.3.el7.x86_64) 7.2 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-123.13.2.el7.x86_64-advanced-fbff9f50-62c3-484e-bca5-d53f672cda7c' {
        ...     load_video
        ...     set gfxpayload=keep
        ...     insmod gzio
        ...     insmod part_msdos
        ...     insmod ext2
        ...     set root='hd0,msdos1'
        ...     if [ x$feature_platform_search_hint = xy ]; then
        ...       search --no-floppy --fs-uuid --set=root --hint-bios=hd0,msdos1 --hint-efi=hd0,msdos1 --hint-baremetal=ahci0,msdos1 --hint='hd0,msdos1'  1184ab74-77b5-4cfa-81d3-fb87b0457577
        ...     else
        ...       search --no-floppy --fs-uuid --set=root 1184ab74-77b5-4cfa-81d3-fb87b0457577
        ...     fi
        ...     linux16 /vmlinuz-3.10.0-327.36.3.el7.x86_64 root=/dev/RHEL7CSB/Root ro rd.lvm.lv=RHEL7CSB/Root rd.luks.uuid=luks-96c66446-77fd-4431-9508-f6912bd84194 crashkernel=128M@16M rd.lvm.lv=RHEL7CSB/Swap vconsole.font=latarcyrheb-sun16 rhgb quiet LANG=en_GB.utf8
        ...     initrd16 /initramfs-3.10.0-327.36.3.el7.x86_64.img
        ...     }
        ... '''.strip()

        >>> from insights.tests import context_wrap
        >>> shared = {Grub2Config: Grub2Config(context_wrap(grub2_content))}
        >>> config = shared[Grub2Config]
        >>> config.boot_entries[0].name
        "'Red Hat Enterprise Linux Workstation (3.10.0-327.36.3.el7.x86_64) 7.2 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-123.13.2.el7.x86_64-advanced-fbff9f50-62c3-484e-bca5-d53f672cda7c'"
        >>> config.boot_entries[0].cmdline
        "linux16 /vmlinuz-3.10.0-327.36.3.el7.x86_64 root=/dev/RHEL7CSB/Root ro rd.lvm.lv=RHEL7CSB/Root rd.luks.uuid=luks-96c66446-77fd-4431-9508-f6912bd84194 crashkernel=128M@16M rd.lvm.lv=RHEL7CSB/Swap vconsole.font=latarcyrheb-sun16 rhgb quiet LANG=en_GB.utf8"
        >>> config['configs']
        [('set pager', '1'), ('/', None)]
        >>> config['menuentry']
        [[('menuentry_name', "'Red Hat Enterprise Linux Workstation (3.10.0-327.36.3.el7.x86_64) 7.2 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-123.13.2.el7.x86_64-advanced-fbff9f50-62c3-484e-bca5-d53f672cda7c'"), ('load_video', None), ('set', 'gfxpayload=keep'), ('insmod', 'gzio'), ('insmod', 'part_msdos'), ('insmod', 'ext2'), ('set', "root='hd0,msdos1'"), ('linux16', '/vmlinuz-3.10.0-327.36.3.el7.x86_64 root=/dev/RHEL7CSB/Root ro rd.lvm.lv=RHEL7CSB/Root rd.luks.uuid=luks-96c66446-77fd-4431-9508-f6912bd84194 crashkernel=128M@16M rd.lvm.lv=RHEL7CSB/Swap vconsole.font=latarcyrheb-sun16 rhgb quiet LANG=en_GB.utf8'), ('initrd16', '/initramfs-3.10.0-327.36.3.el7.x86_64.img')]]
        >>> config.kernel_initrds['grub_kernels'][0]
        'vmlinuz-3.10.0-327.36.3.el7.x86_64'
        >>> config.is_kdump_iommu_enabled
        False
    """
    def __init__(self, *args, **kwargs):
        super(Grub2Config, self).__init__(*args, **kwargs)
        self._version = 2
        self._efi = False
        self.update({'menuentry': self.menuentry})


@parser(Specs.grub2_efi_cfg)
class Grub2EFIConfig(GrubConfig):
    """Parses grub2 configuration for EFI-based systems"""
    def __init__(self, *args, **kwargs):
        super(Grub2EFIConfig, self).__init__(*args, **kwargs)
        self._version = 2
        self._efi = True


@parser(Specs.grub2_grubenv)
class Grub2Grubenv(GrubConfig):
    """
    Parses the ``/boot/grub2/grubenv`` file.

    Attributes:
        name(str): the name of the saved boot entry
        cmdline(str): the cmdline of the saved boot entry
        saved_entry(str): the saved boot entry, alias of the :attr:`self.name`
        kernelopts(dict): the parsed boot options

    Raises:
        SkipException: when input content is empty or no useful data.
        ParseException: when input content is not able to parse.
    """
    def __init__(self, *args, **kwargs):
        super(Grub2Grubenv, self).__init__(*args, **kwargs)
        self._efi = False
        self._version = 2

    def parse_content(self, content):
        """
        Parse the ``/boot/grub2/grubenv``
        """
        if not content:
            raise SkipException("Empty content.")

        self.data = {}
        for line in content:
            if '=' in line:
                key, value = [i.strip() for i in line.split('=', 1)]
                self.data[key] = value
            elif not line.startswith('#'):
                raise ParseException('Bad line: "{0}"'.format(line))

        if not self.data:
            raise SkipException("No useful data")

        self.name = self.saved_entry = self.data.get('saved_entry', '')
        self.cmdline = self.data.get('kernelopts', '')
        self._boot_entries = [BootEntry({'name': self.name, 'cmdline': self.cmdline})]
        self.kernelopts = dict()
        for el in self.cmdline.split():
            key, value = el, True
            if "=" in el:
                key, value = [i.strip() for i in el.split('=', 1)]
            if key not in self.kernelopts:
                self.kernelopts[key] = []
            self.kernelopts[key].append(value)


@parser(Specs.grub2_efi_grubenv)
class Grub2EFIGrubenv(Grub2Grubenv):
    """
    Parses ``/boot/efi/EFI/redhat/grubenv`` for EFI-based systems
    """
    def __init__(self, *args, **kwargs):
        super(Grub2EFIGrubenv, self).__init__(*args, **kwargs)
        self._efi = True


def _parse_config(line):
    """
    Parse configuration lines in grub v1/v2 config
    """
    if "=" not in line:
        return _parse_cmd(line)
    else:
        return _parse_line("=", line)


def _parse_script(list, line, line_iter):
    """
    Eliminate any bash script contained in the grub v2 configuration
    """
    ifIdx = 0
    while (True):
        line = next(line_iter)
        if line.startswith("fi"):
            if ifIdx == 0:
                return
            ifIdx -= 1
        elif line.startswith("if"):
            ifIdx += 1


def _parse_line(sep, line):
    """
    Parse a grub commands/config with format: cmd{sep}opts
    Returns: (name, value): value can be None
    """
    strs = line.split(sep, 1)
    return (strs[0].strip(), None) if len(strs) == 1 else (strs[0].strip(), strs[1].strip())


def _parse_cmd(line):
    """
    Parse commands within grub v1/v2 config using space delimeter
    """
    return _parse_line(" ", line)


def _parse_menu_entry(line_iter, cur_line, conf):
    """
    Parse each `menuentry` that the grub v2 configuration contains
    * Uses "_parse_script" to eliminate bash scripts
    """
    menu = []
    conf['menuentry'].append(menu)
    n, entry = _parse_line("menuentry", cur_line)

    entry_name, v = _parse_line("{", entry)
    if not entry_name:
        raise Exception("Cannot parse menuentry line: {0}".format(cur_line))

    menu.append(('menuentry_name', entry_name))
    if v:
        menu.append(_parse_cmd(v))

    while (True):
        line = next(line_iter)
        if "{" in line:
            n, v = _parse_line("{", line)
            if v:
                menu.append(_parse_cmd(v))
        elif "}" in line:
            n, v = _parse_line("}", line)
            if n:
                menu.append(_parse_cmd(n))
            return
        elif line.startswith("if"):
            _parse_script(menu, line, line_iter)

        else:
            menu.append(_parse_cmd(line))


def _parse_title(line_iter, cur_line, conf):
    """
    Parse "title" in grub v1 config
    """
    title = []
    conf['title'].append(title)
    title.append(('title_name', cur_line.split('title', 1)[1].strip()))
    while (True):
        line = next(line_iter)
        if line.startswith("title "):
            return line

        cmd, opt = _parse_cmd(line)
        title.append((cmd, opt))


def _parse_kernel_initrds_value(line):
    """
    Called by "kernel_initrds" method to parse the kernel and
    initrds lines in the grub v1/v2 config
    """
    return line.split()[0].split('/')[-1]
