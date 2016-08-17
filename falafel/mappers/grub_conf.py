"""

kbase: https://access.redhat.com/solutions/74233
"""
import re
from falafel.core.plugins import mapper
from falafel.core import MapperOutput, computed
from falafel.mappers import get_active_lines

crash_paramater_re = re.compile(r'\bcrashkernel=(\S+)\b')
IOMMU = "intel_iommu=on"


CRASH_KERNEL_OFFSET = 'crash_kernel_offset'
IS_KDUMP_IOMMU_ENABLED = 'is_kdump_iommu_enabled'
KERNEL_INITRD = 'kernel_initrd'
GRUB_KERNELS = 'grub_kernels'
GRUB_INITRDS = 'grub_initrds'


ERROR_KEY_GRUB = "GRUB_CONFIG_ISSUE"
ERROR_KEY_FS = "MISSING_BOOT_FILES"


@mapper('grub2.cfg')
@mapper("grub.conf")
class GrubConfig(MapperOutput):

    @staticmethod
    def parse_content(content):

        data = {}
        data[CRASH_KERNEL_OFFSET]= parse_crash_kernel_offset(content)
        data[IS_KDUMP_IOMMU_ENABLED] = parse_is_kdump_iommu_enabled(content)
        data[KERNEL_INITRD] = parse_kernel_initrd(content)
        return data

    @computed
    def crash_kernel_offset(self):
        return self.data[CRASH_KERNEL_OFFSET]

    @computed
    def is_kdump_iommu_enabled(self):
        return self.data[IS_KDUMP_IOMMU_ENABLED]

    @computed
    def kernels_initrds(self):
        return {GRUB_KERNELS:self.grub_kernels, GRUB_INITRDS: self.grub_initrds} if self.data[KERNEL_INITRD] else None

    @computed
    def grub_kernels(self):
        return self.data[KERNEL_INITRD][GRUB_KERNELS] if self.data[KERNEL_INITRD] else None

    @computed
    def grub_initrds(self):
        return self.data[KERNEL_INITRD][GRUB_INITRDS] if self.data[KERNEL_INITRD] else None




def parse_crash_kernel_offset(data):

    k_list = []
    idx = 0  # if no 'default' in grub.conf, set default to 0
    for line in get_active_lines(data):
        if line.startswith('default'):
            # there are 2 patterns: default=? and default ?
            if '=' in line and len(line.split('=')) >= 2:
                idx = (line.split('=')[1]).strip()
            elif len(line.split()) >= 2:
                idx = (line.split()[1]).strip()
            # Ignore invalid value: defalut=$X
            if idx.isdigit():
                idx = int(idx)
            else:
                idx = -1
            continue
        if line.startswith('kernel'):
            k_list.append(line)

    if idx != -1 and len(k_list) > idx:
        current_kernel = k_list[idx]
        matcher = crash_paramater_re.search(current_kernel)
        crash_kernel_offset = matcher.group(1) if matcher else None
        if crash_kernel_offset and '@' in crash_kernel_offset:
            offset = crash_kernel_offset.split('@')[1]
            if offset and offset not in ['0', '0M']:
                matcher = re.search(r'\d+', offset)
                offset_num = matcher.group() if matcher else None
                if offset_num and offset_num.isdigit() and int(offset_num) <= 16:
                    return crash_kernel_offset

def parse_is_kdump_iommu_enabled(data):
    for line in data:
        if IOMMU in line:
            return True

def _get_grub_entry(line):
    return line.split()[1].split('/')[-1]


def parse_kernel_initrd(data):
    """
        Get the kernel and initrd files referenced in grub.conf
    """

    kernels = []
    initrds = []
    for line in data:
        line = line.strip()
        if line.startswith('module'):
            if 'vmlinuz' in line:
                kernels.append(_get_grub_entry(line))
            elif 'initrd' in line or 'initramfs' in line:
                initrds.append(_get_grub_entry(line))
        elif (line.startswith('kernel') or line.startswith('linux16') or line.startswith('linux')):
            if 'ipxe.lkrn' in line:
                # Machine PXE boots the kernel, assume all is ok
                return
            elif 'xen.gz' not in line:
                kernels.append(_get_grub_entry(line))
        elif line.startswith('initrd') or line.startswith('initrd16'):
            initrds.append(_get_grub_entry(line))

    return {GRUB_KERNELS: kernels, GRUB_INITRDS: initrds}


def _get_grub_entry(line):
    return line.split()[1].split('/')[-1]