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

* For the **configs** dict, the key-value pairs based on the line, split
  on the first '=' character.  If nothing is found after the '=' character,
  then the value is `''`.

* For the **title** and **menuentry** list, dict of each boot entry is stored.

  * The items will be key-value pairs, e.g. ``load_video`` will be stored
    as ``{'load_video': ''}`` and ``set root='hd0,msdos1'`` will be stored
    as ``{'set': "root='hd0,msdos1'"}``.

.. note::
    For GRUB version 2, all lines between the ``if`` and ``fi`` will be ignored
    due to we cannot analyze the result of the bash conditions.

Parsers provided by this module are:

Grub1Config - file ``/boot/grub.conf``
--------------------------------------

Grub1EFIConfig - file ``/boot/efi/EFI/redhat/grub.conf``
--------------------------------------------------------

Grub2Config - file ``/boot/grub/grub2.cfg``
-------------------------------------------

Grub2EFIConfig - file ``/boot/efi/EFI/redhat/grub.cfg``
-------------------------------------------------------

BootLoaderEntries - file ``/boot/loader/entries/*.conf``
--------------------------------------------------------
"""

from insights import Parser
from insights import parser, get_active_lines
from insights.parsers import ParseException, SkipException
from insights.specs import Specs


class BootEntry(dict):
    """
    An object representing a boot entry in the Grub Configuration.

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
                "configs": {
                    name1: [val1, val2, ...]
                    name2: [val],
                    ...
                },
                "title": [
                    {title: name1, kernel: [val], ...},
                    {title: name2, module: [val1, val2], ...},
                ],
                "menuentry": [
                    {menuentry: name1, insmod: [val1, val2], ...},
                    {menuentry: name2, linux16: [val], ...},
                ],
            }

        """

        self.configs = {}
        self._boot_entries = []
        self.entries = self.entries= []
        b_entry = {}
        entry = {}
        in_script = False
        if_idx = 0
        for line_raw in get_active_lines(content):
            # Remove the heading and trailing whitespace and curly brackets
            line = line_raw.strip('{} \t')
            # Skip the stript in Grub2 {
            if line.startswith('if'):
                if_idx += 1
                in_script = True
                continue
            if line.startswith('fi'):
                if_idx -= 1
                in_script = True if if_idx else False
                continue
            # } End of Skip
            # Handle of lines {
            elif not in_script and line:
                # Handle the title / menuentry {
                if line.startswith(('title ', 'menuentry')):
                    self.entries.append(entry) if entry else None
                    self._boot_entries.append(BootEntry(b_entry)) if b_entry else None
                    b_entry = {}
                    entry = {}
                    if line.startswith('title '):
                        name = line.split('title', 1)[1].strip()
                        b_entry['name'] = entry['title'] = name
                    else:
                        name = line.split('menuentry', 1)[1].split('{', 1)[0].strip()
                        if not name:
                            raise ParseException("Cannot parse menuentry line: {0}".format(line_raw))
                        b_entry['name'] = entry['menuentry'] = name
                # } End of title / menuentry handling
                # Inside of an entry {
                elif entry:
                    sp = [i.strip() for i in line.split(None, 1)]
                    val = sp[1] if len(sp) > 1 else ''
                    if sp[0] not in entry:
                        entry[sp[0]] = []
                    # Handle the cmdline {
                    if sp[0].startswith(('kernel', 'linux')):
                        b_entry['cmdline'] = val
                    # } End of cmdline
                    entry[sp[0]].append(val)
                # } End of Inside entry
                # Lines out of entries {
                else:
                    se = line.find('=')
                    ss = line.find(' ')
                    sep = '=' if (0 < se > ss) or (ss < 0 < se) else None
                    sp = [i.strip() for i in line.split(sep, 1)]
                    if sp[0] not in self.configs:
                        self.configs[sp[0]] = []
                    self.configs[sp[0]].append(sp[1] if len(sp) > 1 else '')
                # } End of Out of entry
            # } End of lines handling
        # Store the last entry
        self.entries.append(entry) if entry else None
        self.boot_entries.append(BootEntry(b_entry)) if b_entry else None

        self.update({'configs': self.configs}) if self.configs else None

        self._is_kdump_iommu_enabled_ = self._is_kdump_iommu_enabled()
        name_values = []
        for k, v in self.configs.items():
            if (k.startswith(('module', 'kernel', 'linux', 'initrd'))):
                name_values.append((k, v))
        for entry in self.entries:
            for k, v in entry.items():
                if (k.startswith(('module', 'kernel', 'linux', 'initrd'))):
                    name_values.append((k, v))
        self._kernel_initrds = get_kernel_initrds(name_values)

    def _is_kdump_iommu_enabled(self):
        for l in self._boot_entries:
            if "intel_iommu=on" in l.get('cmdline', ''):
                return True
        return False

    @property
    def boot_entries(self):
        """
        Get all boot entries in GRUB configuration.

        Returns:
            (list): A list of dict for each boot entry in below format:
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
        return self._is_kdump_iommu_enabled_

    @property
    def kernel_initrds(self):
        """
        Get the `kernel` and `initrd` files referenced in GRUB configuration files

        Returns:
            (dict): Returns a dict of the `kernel` and `initrd` files referenced
                    in GRUB configuration files
        """
        return self._kernel_initrds


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
        [('title', 'Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64)'), ('kernel', '/vmlinuz-2.6.32-431.17.1.el6.x86_64 crashkernel=128M rhgb quiet')]
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
        self.update({'title': self.entries})

    def get_current_title(self):
        """
        Get the current default title from the ``default`` option in the
        main configuration. (GRUB v1 only)

        Returns:
            list: A list contains all settings of the default boot entry:
                  - [(title, name), (cmd, opt), (cmd, opt) ...]
        """
        # if no 'default' in grub.conf, set default to 0
        idx = '0'
        for k, v in self.configs.items():
            if k == 'default':
                idx = v[-1]
                break

        if idx.isdigit():
            idx = int(idx)
            if len(self.entries) > idx:
                return self.entries[idx]

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
        [[('menuentry', "'Red Hat Enterprise Linux Workstation (3.10.0-327.36.3.el7.x86_64) 7.2 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-123.13.2.el7.x86_64-advanced-fbff9f50-62c3-484e-bca5-d53f672cda7c'"), ('load_video', None), ('set', 'gfxpayload=keep'), ('insmod', 'gzio'), ('insmod', 'part_msdos'), ('insmod', 'ext2'), ('set', "root='hd0,msdos1'"), ('linux16', '/vmlinuz-3.10.0-327.36.3.el7.x86_64 root=/dev/RHEL7CSB/Root ro rd.lvm.lv=RHEL7CSB/Root rd.luks.uuid=luks-96c66446-77fd-4431-9508-f6912bd84194 crashkernel=128M@16M rd.lvm.lv=RHEL7CSB/Swap vconsole.font=latarcyrheb-sun16 rhgb quiet LANG=en_GB.utf8'), ('initrd16', '/initramfs-3.10.0-327.36.3.el7.x86_64.img')]]
        >>> config.kernel_initrds['grub_kernels'][0]
        'vmlinuz-3.10.0-327.36.3.el7.x86_64'
        >>> config.is_kdump_iommu_enabled
        False
    """
    def __init__(self, *args, **kwargs):
        super(Grub2Config, self).__init__(*args, **kwargs)
        self._version = 2
        self._efi = False
        self.update({'menuentry': self.entries})


@parser(Specs.grub2_efi_cfg)
class Grub2EFIConfig(Grub2Config):
    """Parses grub2 configuration for EFI-based systems"""
    def __init__(self, *args, **kwargs):
        super(Grub2EFIConfig, self).__init__(*args, **kwargs)
        self._version = 2
        self._efi = True


@parser(Specs.boot_loader_entries)
class BootLoaderEntries(Parser, dict):
    """
    Parses the ``/boot/loader/entries/*.conf`` files.

    Attributes:
        title(str): the name of the boot entry
        cmdline(str): the cmdline of the saved boot entry

    Raises:
        SkipException: when input content is empty or no useful data.
    """
    def parse_content(self, content):
        """
        Parses the ``/boot/loader/entries/*.conf`` files.
        """
        if not content:
            raise SkipException()

        self.entry = {}
        self.title = ''
        self.cmdline = ''
        for line in content:
            key, value = [i.strip() for i in line.split(None, 1)]
            self.entry[key] = value
            if key == 'options':
                self.cmdline = value

        if not self.entry:
            raise SkipException()

        self.update(self.entry)
        self.title = self.entry.get('title')
        self.is_kdump_iommu_enabled = "intel_iommu=on" in self.cmdline


def get_kernel_initrds(name_values):
    kernels = []
    initrds = []
    for name, value in name_values:
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
    return {'grub_kernels': kernels, 'grub_initrds': initrds}
