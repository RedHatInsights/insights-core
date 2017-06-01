"""
GRUB configuration - files `/boot/grub/grub2.cfg`
=======================================================================

This parser reads the configuration of the GRand Unified Bootloader, version
2.

This is currently a fairly simple parsing process.  Data read from the file
is put into roughly three categories:

* **configs**: lines read from the file that aren't boot options (i.e.
  excluding lines that go in the *menuentry* sections).  These
  are split into pairs on the first '=' sign.
* **menuentry**: lines prefixed by the word 'menuentry'.  All following lines
  up to the line starting with '}' are treated as part of one menu entry.

Each of these categories is (currently) stored as a simple list of tuples.

* For the list of **configs**, the tuples are (key, value) pairs based on
  the line, split on the first '=' character.  If nothing is found after the
  '=' character, then the value is ``None``. This is mostly unusable
  (outside of the set pager=1 config parameter) since most of it is bash
  script.

* For the **menuentry** list:

  * the first item will be a tuple of two items: 'menuentry_name' and the
    full text between 'menuentry' and '{'.
  * the rest of the items will be tuples of that line in the menu entry
    configuration, split on the first space.  If no space is found after the
    first word, the value will be ``None``.  So ``load_video`` will be stored
    as ``('load_video', None)`` and ``set root='hd0,msdos1'`` will be stored
    as ``('set', "root='hd0,msdos1'")``.

There are functions for dealing with the 'crashkernel' option and
usage of the Intel IOMMU, however at this time these return None for
Grub v2 configurations. These remain exposed to stay consitent with Grub v1.
Making these two features fully functional should be addressed in the future.

Helper functions can be used for extracting the kernel and initrd
configurations available.

Sample input data is provided in the example below.

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
    ... '''.strip()

    >>> from insights.tests import context_wrap
    >>> shared = {Grub2Config: Grub2Config(context_wrap(grub2_content))}
    >>> config = shared[Grub2Config]
    >>> config['configs']
    [('set pager', '1'), ('/', None)]
    >>> config['menuentry']
    [[('menuentry_name', "'Red Hat Enterprise Linux Workstation (3.10.0-327.36.3.el7.x86_64) 7.2 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-123.13.2.el7.x86_64-advanced-fbff9f50-62c3-484e-bca5-d53f672cda7c'"), ('load_video', None), ('set', 'gfxpayload=keep'), ('insmod', 'gzio'), ('insmod', 'part_msdos'), ('insmod', 'ext2'), ('set', "root='hd0,msdos1'"), ('linux16', '/vmlinuz-3.10.0-327.36.3.el7.x86_64 root=/dev/RHEL7CSB/Root ro rd.lvm.lv=RHEL7CSB/Root rd.luks.uuid=luks-96c66446-77fd-4431-9508-f6912bd84194 crashkernel=128M@16M rd.lvm.lv=RHEL7CSB/Swap vconsole.font=latarcyrheb-sun16 rhgb quiet LANG=en_GB.utf8'), ('initrd16', '/initramfs-3.10.0-327.36.3.el7.x86_64.img')]]
    >>> config.kernels_initrds['grub_kernels'][0]
    'vmlinuz-3.10.0-327.36.3.el7.x86_64'
"""

from .. import Parser, parser, get_active_lines, defaults, LegacyItemAccess
from insights.parsers import ParseException

IOMMU = "intel_iommu=on"

KERNEL_INITRD = 'kernel_initrd'
GRUB_KERNELS = 'grub_kernels'
GRUB_INITRDS = 'grub_initrds'


@parser('grub2.cfg')
class Grub2Config(LegacyItemAccess, Parser):
    """
    Parser for configuration for GRUB version 2.
    """

    def parse_content(self, content):
        """
        Parse grub config file to create a dict with this structure::

            {
                "configs": [ (name, value), (name, value) ...],
                "menuentry": [
                    [(menuentry_name, its name), (cmd, opt), (cmd, opt) ...],
                    [another menu entry]
                ],
            }
        """
        line_iter = iter(get_active_lines(content))
        conf = {"configs": [], "menuentry": []}
        line = None
        while (True):
            try:

                if line is None:
                    line = line_iter.next()
                if line.startswith('title '):
                    raise ParseException("Cannot process Grub v1 file in Grub2Config parser. Please use Grub1Config parser Original line = [%s]".format(line))
                elif line.startswith('menuentry '):
                    _parse_menu_entry(line_iter, line, conf)
                    line = None
                else:
                    if line.startswith("if"):
                        # conf["configs"].append(_parse_line("\n", line))
                        _parse_script(conf["configs"], line, line_iter)
                    else:
                        conf["configs"].append(_parse_config(line))
                    line = None

            except StopIteration:
                self.data = conf
                return

    @property
    @defaults()
    def kernels_initrds(self):
        """
            Get the kernel and initrd files referenced in grub.conf
        """

        kernels = []
        initrds = []
        name_values = [(k, v) for k, v in self.data.get('configs', [])]
        for value in self.data.get("menuentry", []):
            name_values.extend(value)

        for name, value in name_values:

            if (name.startswith('linux')):
                if 'ipxe.lkrn' in value:
                    # Machine PXE boots the kernel, assume all is ok
                    return
                elif 'xen.gz' not in value:
                    kernels.append(_parse_kernels_initrds_value(value))
            elif name.startswith('initrd'):
                initrds.append(_parse_kernels_initrds_value(value))

        return {GRUB_KERNELS: kernels, GRUB_INITRDS: initrds}


def _parse_line(sep, line):
    """
    Parse a grub v2 commands/config with format: cmd{sep}opts
    Returns: (name, value): value can be None
    """
    strs = line.split(sep, 1)
    return (strs[0].strip(), None) if len(strs) == 1 else (strs[0].strip(), strs[1].strip())


def _parse_cmd(line):
    """
    Parse commands within grub v2 config using space delimeter
    """
    return _parse_line(" ", line)


def _parse_config(line):
    """
    Parse configuration lines in grub v2 config
    """
    if "=" not in line:
        return _parse_cmd(line)
    else:
        return _parse_line("=", line)


def _parse_script(list, line, line_iter):
    """
    Parse and eliminate any bash script contained in the
    grub v2 config
    """
    _parse_line("\n", line)
    ifIdx = 0
    while (True):
        line = line_iter.next()
        if line.startswith("fi"):
            if ifIdx == 0:
                return
        elif line.startswith("if"):
            ++ifIdx


def _parse_menu_entry(line_iter, cur_line, conf):
    """
    Parse all of the menuentries the the grub v2 config contains
      Uses "_parse_script" to eliminate bas scripts
    """
    menu = []
    conf['menuentry'].append(menu)
    n, entry = _parse_line("menuentry", cur_line)
    if not entry:
        raise ParseException("Cannot parse menuentry line. Original line = [%s]".format(cur_line))

    entry_name, v = _parse_line("{", entry)
    if entry_name is None:
        raise ParseException("Cannot parse menuentry line. Original line = [%s]".format(cur_line))
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
        elif line.startswith("if"):
            _parse_script(menu, line, line_iter)

        else:
            menu.append(_parse_cmd(line))


def _parse_kernels_initrds_value(line):
    """
    Called by "kernels_initrds" method to parse the kernel and
    initrds lines  in the grub v2 config
    """
    return line.split()[0].split('/')[-1]


@parser('grub2-efi.cfg')
class Grub2EFIConfig(Grub2Config):
    """Parses grub2 configuration for EFI-based systems"""
    pass


if __name__ == "__main__":
    import doctest
    doctest.testmod()
