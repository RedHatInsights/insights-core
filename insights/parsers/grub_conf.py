"""
GRUB configuration - files `/boot/grub/grub2.cfg` and `/boot/grub.conf`
=======================================================================

This parser reads the configuration of the GRand Unified Bootloader, versions
1 or 2.

This is currently a fairly simple parsing process.  Data read from the file
is put into roughly three categories:

* **configs**: lines read from the file that aren't boot options (i.e.
  excluding lines that go in the *title* and *menuentry* sections).  These
  are split into pairs on the first '=' sign.
* **title**: lines prefixed by the word 'title'.  All following lines up to
  the next title line are folded together.
* **menuentry**: lines prefixed by the word 'menuentry'.  All following lines
  up to the line starting with '}' are treated as part of one menu entry.

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

There are several helper functions for dealing with the 'crashkernel' option,
usage of the Intel IOMMU, and for extracting the kernel and initrd
configurations available.

With an example ``/boot/grub.conf`` configuration file of::

    default=0
    timeout=0
    splashimage=(hd0,0)/grub/splash.xpm.gz
    hiddenmenu
    title Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64)
            kernel /vmlinuz-2.6.32-431.17.1.el6.x86_64 crashkernel=128M rhgb quiet
    title Red Hat Enterprise Linux Server (2.6.32-431.11.2.el6.x86_64)
            kernel /vmlinuz-2.6.32-431.11.2.el6.x86_64 crashkernel=128M rhgb quiet

The following code will extract relevant information from the GRUB
configuration::

    >>> config = shared[GrubConfig]
    >>> config['configs']
    [ ('default', '1'),
      ('timeout', '0'),
      ('splashimage', '(hd0,0)/grub/splash.xpm.gz'),
      ('hiddenmenu', None)
    ]
    >>> config['title'][0]
    [ ('title', 'Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64'),
      ('kernel', '/vmlinuz-2.6.32-431.17.1.el6.x86_64 crashkernel=128M rhgb quiet') ]
    >>> config['title'][1][0][1]
    'Red Hat Enterprise Linux Server (2.6.32-431.11.2.el6.x86_64)'
    >>> config['menuconfig'] # an empty list here shows GRUB v1 config
    []
    >>> config.crash_kernel_offset
    None
    >>> config.is_kdump_iommu_enabled
    None
    >>> config.kernel_initrds['grub_kernels'][0]
    'vmlinuz-2.6.32-431.17.1.el6.x86_64'
"""

import re
from .. import Parser, parser, get_active_lines, defaults, LegacyItemAccess

crash_paramater_re = re.compile(r'\bcrashkernel=(\S+)\b')
IOMMU = "intel_iommu=on"


CRASH_KERNEL_OFFSET = 'crash_kernel_offset'
IS_KDUMP_IOMMU_ENABLED = 'is_kdump_iommu_enabled'
KERNEL_INITRD = 'kernel_initrd'
GRUB_KERNELS = 'grub_kernels'
GRUB_INITRDS = 'grub_initrds'
GRUB_BOUNDARY_WORDS = ['title', 'menuentry', '}']


class GrubConfParserException(Exception):
    pass


@parser('grub2.cfg')
@parser("grub.conf")
class GrubConfig(LegacyItemAccess, Parser):
    """
    Parser for configuration for both GRUB versions 1 and 2.
    """

    def parse_content(self, content):
        """
        Parse grub config file to create a dict with this structure::

            {
                "configs": [ (name, value), (name, value) ...],
                "title": [
                    [(title_name, its name), (cmd, opt), (cmd, opt) ...],
                    [(another title, name), ...]
                ],
                "menuentry": [
                    [(menuentry_name, its name), (cmd, opt), (cmd, opt) ...],
                    [another menu entry]
                ],
            }
        """
        line_iter = iter(get_active_lines(content))
        conf = {"configs": [], "title": [], "menuentry": []}
        line = None
        while (True):
            try:

                if line is None:
                    line = line_iter.next()

                if line.startswith('title '):
                    last_line = _parse_title(line_iter, line, conf)
                    line = last_line
                elif line.startswith('menuentry '):
                    _parse_menu_entry(line_iter, line, conf)
                    line = None
                else:
                    conf["configs"].append(_parse_config(line))
                    line = None

            except StopIteration:
                self.data = conf
                return

    @property
    @defaults()
    def crash_kernel_offset(self):
        """
        Finds the current default title, looks for the 'crashkernel' option,
        and looks for any offset (i.e. '@16M') in the value.  If this is
        present, and is greater than zero, the value is returned.  Otherwise,
        the returned value is ``None``.
        """

        current_title = self._get_current_title()
        if not current_title:
            return None

        for k in current_title:
            if k[0] == 'kernel':
                kernel_val = k[1]
                if kernel_val:
                    matcher = crash_paramater_re.search(kernel_val)
                    crash_kernel_offset = matcher.group(1) if matcher else None
                    if crash_kernel_offset and '@' in crash_kernel_offset:
                        offset = crash_kernel_offset.split('@')[1]
                        if offset and offset not in ['0', '0M']:
                            matcher = re.search(r'\d+', offset)
                            offset_num = matcher.group() if matcher else None
                            if offset_num and offset_num.isdigit() and int(offset_num) <= 16:
                                return crash_kernel_offset

    def _get_current_title(self):
        """
        Returns the current default title from the ``default`` option in the
        main configuration.
        """
        if "configs" in self.data:
            conf = self.data["configs"]
            # if no 'default' in grub.conf, set default to 0
            idx = next((v[1] for i, v in enumerate(conf) if v[0] == 'default'), '0')

            if idx.isdigit():
                idx = int(idx)
            else:
                return None

            title = self.data['title']
            if len(title) > idx:
                return title[idx]

    @property
    @defaults()
    def is_kdump_iommu_enabled(self):
        """
        Does any kernel have 'intel_iommu=on' set?
        """

        for title in self.data['title']:
            for k in title:
                if k[0] == 'kernel' and IOMMU in k[1]:
                    return True

    @property
    @defaults()
    def kernels_initrds(self):
        """
            Get the kernel and initrd files referenced in grub.conf
        """

        kernels = []
        initrds = []
        name_values = [(k, v) for k, v in self.data.get('configs', [])]
        for value in self.data.get("title", []) + self.data.get("menuentry", []):
            name_values.extend(value)

        for name, value in name_values:
            if name.startswith('module'):
                if 'vmlinuz' in value:
                    kernels.append(_parse_kernels_initrds_value(value))
                elif 'initrd' in value or 'initramfs' in value:
                    initrds.append(_parse_kernels_initrds_value(value))
            elif (name.startswith('kernel') or name.startswith('linux16') or name.startswith('linux')):
                if 'ipxe.lkrn' in value:
                    # Machine PXE boots the kernel, assume all is ok
                    return
                elif 'xen.gz' not in value:
                    kernels.append(_parse_kernels_initrds_value(value))
            elif name.startswith('initrd') or name.startswith('initrd16'):
                initrds.append(_parse_kernels_initrds_value(value))

        return {GRUB_KERNELS: kernels, GRUB_INITRDS: initrds}


def _parse_line(sep, line):
    """
        parse a grub commands/config with format: cmd{sep}opts
    Returns: (name, value): value can be None
    """
    strs = line.split(sep, 1)
    return (strs[0].strip(), None) if len(strs) == 1 else (strs[0].strip(), strs[1].strip())


def _parse_cmd(line):
    return _parse_line(" ", line)


def _parse_config(line):
    return _parse_line("=", line)


def _parse_title(line_iter, cur_line, conf):
    title = []
    conf['title'].append(title)
    title.append(('title_name', cur_line.split('title', 1)[1].strip()))
    while (True):
        line = line_iter.next()
        if line.startswith("title") or line.startswith("menuentry"):
            return line

        cmd, opt = _parse_cmd(line)
        title.append((cmd, opt))


def _parse_menu_entry(line_iter, cur_line, conf):
    menu = []
    conf['menuentry'].append(menu)
    n, entry = _parse_line("menuentry", cur_line)
    if not entry:
        raise GrubConfParserException("Cannot parse menuentry line. Original line = [%s]".format(cur_line))

    entry_name, v = _parse_line("{", entry)
    if entry_name is None:
        raise GrubConfParserException("Cannot parse menuentry line. Original line = [%s]".format(cur_line))
    menu.append(('menuentry_name', entry_name))
    if v:
        menu.append(_parse_cmd(v))

    while (True):
        line = line_iter.next()
        if "{" in line:
            n, v = _parse_line("{", line)
            if v:
                menu.append(_parse_cmd(v))
        elif "}" in line:
            n, v = _parse_line("}", line)
            if n:
                menu.append(_parse_cmd(n))
            return
        else:
            menu.append(_parse_cmd(line))


def _parse_kernels_initrds_value(line):
    return line.split()[0].split('/')[-1]
