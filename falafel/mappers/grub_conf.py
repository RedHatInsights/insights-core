"""

kbase: https://access.redhat.com/solutions/74233
"""
import re
from falafel.core.plugins import mapper
from falafel.core import MapperOutput, computed
from falafel.mappers import get_active_lines

from collections import defaultdict

crash_paramater_re = re.compile(r'\bcrashkernel=(\S+)\b')
IOMMU = "intel_iommu=on"


CRASH_KERNEL_OFFSET = 'crash_kernel_offset'
IS_KDUMP_IOMMU_ENABLED = 'is_kdump_iommu_enabled'
KERNEL_INITRD = 'kernel_initrd'
GRUB_KERNELS = 'grub_kernels'
GRUB_INITRDS = 'grub_initrds'


ERROR_KEY_GRUB = "GRUB_CONFIG_ISSUE"
ERROR_KEY_FS = "MISSING_BOOT_FILES"

GRUB_BOUNDARY_WORDS = ['title', 'menuentry', '}']


class GrubConfParserException(Exception):
    pass


@mapper('grub2.cfg')
@mapper("grub.conf")
class GrubConfig(MapperOutput):

    @staticmethod
    def parse_content(content):
        """
        Parse grub config file to create a dict with this structure:
        {
            "configs": [ (name, value), (name, value) ....],
            "title": [ [(title_name, its name), (cmd, opt), (cmd, opt) ...], [another title] ]
            "menuentry": [ [(menuentry_name, its name), (cmd, opt), (cmd, opt) ...], [another menu entry] ]
        }
        """
        iterator = iter(get_active_lines(content))
        conf = defaultdict(list)
        line = None
        while (True):
            try:

                if line is None:
                    line = iterator.next()

                if line.startswith('title'):
                    last_line = _parse_title(iterator, line, conf)
                    line = last_line
                elif line.startswith('menuentry'):
                    _parse_menu_entry(iterator, line, conf)
                    line = None
                else:
                    conf["configs"].append(_parse_config(line))
                    line = None

            except StopIteration:
                return conf

    @computed
    def crash_kernel_offset(self):

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

    @computed
    def is_kdump_iommu_enabled(self):

        for title in self.data['title']:
            for k in title:
                if k[0] == 'kernel' and IOMMU in k[1]:
                    return True

    @computed
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


def _parse_title(iter, cur_line, conf):
    title = []
    conf['title'].append(title)
    title.append(('title_name', cur_line.split('title', 1)[1].strip()))
    while (True):
        line = iter.next()
        if not line or line.startswith("title") or line.startswith("menuentry"):
            return line

        cmd, opt = _parse_cmd(line)
        title.append((cmd, opt))


def _parse_menu_entry(iter, cur_line, conf):
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
        line = iter.next()
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
