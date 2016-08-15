import unittest
from falafel.mappers.grub_conf import GrubConfig

from falafel.tests import context_wrap


IOMMU_OFF = ["kernel /vmlinuz-2.6.32-279.el6.x86_64 ro root=/dev/mapper/vg00-lv00 intel_iommu=off rd_LVM_LV=vg00/lv00 crashkernel=256M@16M"]
IOMMU_MISSING = ["kernel /vmlinuz-2.6.32-279.el6.x86_64 ro root=/dev/mapper/vg00-lv00 rd_LVM_LV=vg00/lv00 crashkernel=256M@16M"]
IOMMU_ON = ["kernel /vmlinuz-2.6.32-279.el6.x86_64 ro root=/dev/mapper/vg00-lv00 intel_iommu=on rd_LVM_LV=vg00/lv00 crashkernel=256M@16M"]

class TestKdumpIommu(unittest.TestCase):

    def test_kdump_iommu_enabled(self):
        self.assertEquals(None, GrubConfig.parse_context(context_wrap(IOMMU_OFF)).is_kdump_iommu_enabled)
        self.assertEquals(None, GrubConfig.parse_context(context_wrap(IOMMU_MISSING)).is_kdump_iommu_enabled)
        self.assertTrue(GrubConfig.parse_context(context_wrap(IOMMU_ON)).is_kdump_iommu_enabled)
