"""

kbase: https://access.redhat.com/solutions/74233
"""
import re
from falafel.core.plugins import mapper
from falafel.core import MapperOutput, computed

crash_paramater_re = re.compile(r'\bcrashkernel=(\S+)\b')
IOMMU = "intel_iommu=on"

@mapper("grub.conf")
class GrubConfig(MapperOutput):

    @classmethod
    def parse_context(cls, context):
        return cls(context.data, context.path)

    @computed
    def crash_kernel_offset(self):

        k_list = []
        idx = 0  # if no 'default' in grub.conf, set default to 0
        for line in self.data:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
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

    @computed
    def is_kdump_iommu_enabled(self):
        for line in self.data:
            if IOMMU in line:
                return True