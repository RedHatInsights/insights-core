import unittest
from falafel.mappers.grub_conf import GrubConfig
from falafel.tests import context_wrap

BAD_DEFAULT_1 = """
#boot=/dev/sda

default=${last}
timeout=0
splashimage=(hd0,0)/grub/splash.xpm.gz
hiddenmenu
title Red Hat Enterprise Linux Server (2.6.32-431.11.2.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.11.2.el6.x86_64 crashkernel=128M@8M rhgb quiet
""".strip()

GOOD_OFFSET_4 = """
#boot=/dev/sda

default 1
timeout=0
splashimage=(hd0,0)/grub/splash.xpm.gz
hiddenmenu
title Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.17.1.el6.x86_64 crashkernel=  rhgb quiet
title Red Hat Enterprise Linux Server (2.6.32-431.11.2.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.11.2.el6.x86_64 crashkernel=128M@32M rhgb quiet
""".strip()

GOOD_OFFSET_3 = """
#boot=/dev/sda
default=1
timeout=0
splashimage=(hd0,0)/grub/splash.xpm.gz
hiddenmenu
title Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.17.1.el6.x86_64 crashkernel=128M@0  rhgb quiet
title Red Hat Enterprise Linux Server (2.6.32-431.11.2.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.11.2.el6.x86_64 crashkernel=128M@0 rhgb quiet
""".strip()

GOOD_OFFSET_2 = """
#boot=/dev/sda

default=1
timeout=0
splashimage=(hd0,0)/grub/splash.xpm.gz
hiddenmenu
title Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.17.1.el6.x86_64 crashkernel=128M@0M  rhgb quiet
title Red Hat Enterprise Linux Server (2.6.32-431.11.2.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.11.2.el6.x86_64 crashkernel=128M@0M rhgb quiet
""".strip()

GOOD_OFFSET_1 = """
#boot=/dev/sda
default=0
timeout=0
splashimage=(hd0,0)/grub/splash.xpm.gz
hiddenmenu
title Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.17.1.el6.x86_64 crashkernel=128M rhgb quiet
title Red Hat Enterprise Linux Server (2.6.32-431.11.2.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.11.2.el6.x86_64 crashkernel=128M rhgb quiet
""".strip()

BAD_OFFSET = """
#boot=/dev/sda

default=1
timeout=0
splashimage=(hd0,0)/grub/splash.xpm.gz
hiddenmenu
title Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.17.1.el6.x86_64 crashkernel=  rhgb quiet
title Red Hat Enterprise Linux Server (2.6.32-431.11.2.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.11.2.el6.x86_64 crashkernel=128M@16M rhgb quiet
""".strip()

NOMATCH_MEMORY = """
#boot=/dev/sda
default=1
timeout=0
splashimage=(hd0,0)/grub/splash.xpm.gz
hiddenmenu
title Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.17.1.el6.x86_64 rhgb quiet
title Red Hat Enterprise Linux Server (2.6.32-431.11.2.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.11.2.el6.x86_64 crashkernel=128M@M rhgb quiet
""".strip()

NOMATCH_CRASH_PARAM = """
#boot=/dev/sda
default=1
timeout=0
splashimage=(hd0,0)/grub/splash.xpm.gz
hiddenmenu
title Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.17.1.el6.x86_64 rhgb quiet
title Red Hat Enterprise Linux Server (2.6.32-431.11.2.el6.x86_64)
        kernel /vmlinuz-2.6.32-431.11.2.el6.x86_64 rhgb quiet
""".strip()

IOMMU_OFF = """
title Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64)
    kernel /vmlinuz-2.6.32-279.el6.x86_64 ro root=/dev/mapper/vg00-lv00 intel_iommu=off rd_LVM_LV=vg00/lv00 crashkernel=256M@16M
"""
IOMMU_MISSING = """
title Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64)
    kernel /vmlinuz-2.6.32-279.el6.x86_64 ro root=/dev/mapper/vg00-lv00 rd_LVM_LV=vg00/lv00 crashkernel=256M@16M
"""
IOMMU_ON = """
title Red Hat Enterprise Linux Server (2.6.32-431.17.1.el6.x86_64)
    kernel /vmlinuz-2.6.32-279.el6.x86_64 ro root=/dev/mapper/vg00-lv00 intel_iommu=on rd_LVM_LV=vg00/lv00 crashkernel=256M@16M
"""


class TestGrubConfKdump(unittest.TestCase):

    def test_check_offset(self):
        print GrubConfig(context_wrap(GOOD_OFFSET_1)).crash_kernel_offset
        assert GrubConfig(context_wrap(GOOD_OFFSET_1)).crash_kernel_offset is None
        assert GrubConfig(context_wrap(GOOD_OFFSET_2)).crash_kernel_offset is None
        assert GrubConfig(context_wrap(GOOD_OFFSET_3)).crash_kernel_offset is None
        assert GrubConfig(context_wrap(GOOD_OFFSET_4)).crash_kernel_offset is None
        assert GrubConfig(context_wrap(BAD_DEFAULT_1)).crash_kernel_offset is None
        assert "128M@16M" == GrubConfig(context_wrap(BAD_OFFSET)).crash_kernel_offset

    def test_nonetype_group(self):
        """
        Check that a search has a non-None result before attempting to get the ``group``.

        See https://projects.engineering.redhat.com/browse/CEECBA-1239
        """
        assert GrubConfig(context_wrap(NOMATCH_CRASH_PARAM)).crash_kernel_offset is None
        assert GrubConfig(context_wrap(NOMATCH_MEMORY)).crash_kernel_offset is None

    def test_kdump_iommu_enabled(self):
        assert GrubConfig(context_wrap(IOMMU_OFF)).is_kdump_iommu_enabled is None
        assert GrubConfig(context_wrap(IOMMU_MISSING)).is_kdump_iommu_enabled is None
        assert GrubConfig(context_wrap(IOMMU_ON)).is_kdump_iommu_enabled is True
