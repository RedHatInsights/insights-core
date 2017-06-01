"""
GRUB configuration - files `/boot/grub1.conf`
=======================================================================

This parser reads the configuration of the GRand Unified Bootloader, version
1.

This is currently a fairly simple parsing process.  Data read from the file
is put into roughly three categories:

* **configs**: lines read from the file that aren't boot options (i.e.
  excluding lines that go in the *title* section).  These
  are split into pairs on the first '=' sign.
* **title**: lines prefixed by the word 'title'.  All following lines up to
  the next title line are folded together.

Each of these categories is (currently) stored as a simple list of tuples.

* For the list of **configs**, the tuples are (key, value) pairs based on
  the line, split on the first '=' character.  If nothing is found after the
  '=' character, then the value is ``None``.
* For the **title** list, there will be exactly two items in this list:

  * The first item will be a tuple of two items: 'title_name' and the
    title of the boot option.
  * The second item will be a tuple of two items: 'kernel' and the entire
    rest of the kernel boot line as if it had been given all on one line.

There are several helper functions for dealing with the usage of the Intel IOMMU,
and for extracting the kernel and initrd
configurations available.

Sample input data is provided in the example below.

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
    >>> config.is_kdump_iommu_enabled
    >>> config.kernels_initrds['grub_kernels'][0]
    'vmlinuz-2.6.32-431.17.1.el6.x86_64'
"""

from .. import Parser, parser, get_active_lines, defaults, LegacyItemAccess
from insights.parsers import ParseException

IOMMU = "intel_iommu=on"
IS_KDUMP_IOMMU_ENABLED = 'is_kdump_iommu_enabled'
KERNEL_INITRD = 'kernel_initrd'
GRUB_KERNELS = 'grub_kernels'
GRUB_INITRDS = 'grub_initrds'


@parser("grub.conf")
class Grub1Config(LegacyItemAccess, Parser):
    """
    Parser for configuration for GRUB version 1.
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
            }
        """
        line_iter = iter(get_active_lines(content))
        conf = {"configs": [], "title": []}
        line = None
        while (True):
            try:

                if line is None:
                    line = line_iter.next()

                if line.startswith('menuentry '):
                    raise ParseException("Cannot process Grub v2 file in Grub1Config parser. Please use Grub2Config parser Original line = [%s]".format(line))
                elif line.startswith('title '):
                    last_line = _parse_title(line_iter, line, conf)
                    line = last_line
                else:
                    conf["configs"].append(_parse_config(line))
                    line = None

            except StopIteration:
                self.data = conf
                return

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
        for value in self.data.get("title", []):
            name_values.extend(value)

        for name, value in name_values:
            if name.startswith('module'):
                if 'vmlinuz' in value:
                    kernels.append(_parse_kernels_initrds_value(value))
                elif 'initrd' in value:
                    initrds.append(_parse_kernels_initrds_value(value))
            elif (name.startswith('kernel')):
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
        parse a grub commands/config with format: cmd{sep}opts
    Returns: (name, value): value can be None
    """
    strs = line.split(sep, 1)
    return (strs[0].strip(), None) if len(strs) == 1 else (strs[0].strip(), strs[1].strip())


def _parse_cmd(line):
    """
    Parse commands within grub v1 config using space delimeter
    """
    return _parse_line(" ", line)


def _parse_config(line):
    """
    Parse configuration lines in grub v1 config
    """
    return _parse_line("=", line)


def _parse_title(line_iter, cur_line, conf):
    """
    Parse "tite" in grub v1 config
    """
    title = []
    conf['title'].append(title)
    title.append(('title_name', cur_line.split('title', 1)[1].strip()))
    while (True):
        line = line_iter.next()
        if line.startswith("title"):
            return line

        cmd, opt = _parse_cmd(line)
        title.append((cmd, opt))


def _parse_kernels_initrds_value(line):
    """
    Called by "kernels_initrds" method to parse the kernel and
    initrds lines  in the grub v1 config
    """
    return line.split()[0].split('/')[-1]


if __name__ == "__main__":
    import doctest
    doctest.testmod()
