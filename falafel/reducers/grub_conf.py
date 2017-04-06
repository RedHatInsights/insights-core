"""
Shared reducer for grub v1 and v2 configs
=========================================

Shared reducer for Red Hat Grub v1 and Grub v2 information.
This reducer uses bot the Grb1Config and the Grub2Config mappers.
It determines which mapper was used by checking the class atribute in shared.
When the appropriate Grub mapper class is determined it executes the reducer
method for that class.
Successful completion of the reducer yields the following information
kernel_initrds - list of kernel_initrds for in the configuration file
is_kdump_iommu_enabled - returns true if any kernel entry in the list of titles has
kdump_iommu_enabled (Grub v1 only). Grub v2 will return False.


Examples:
    >>> GRUB1_TEMPLATE = '''
    ... default=0
    ... timeout=5
    ... splashimage=(hd0,0)/grub/splash.xpm.gz
    ... hiddenmenu
    ... title Red Hat Enterprise Linux 6 (2.6.32-642.el6.x86_64)
    ...            root (hd0,0)
    ...            kernel /vmlinuz-2.6.32-642.el6.x86_64 {kernel_boot_options} ro root=/dev/mapper/VolGroup-lv_root intel_iommu=off rd_NO_LUKS LANG=en_US.UTF-8 rd_NO_MD rd_LVM_LV=VolGroup/lv_swap SYSFONT=latarcyrheb-sun16 crashkernel=auto rd_LVM_LV=VolGroup/lv_root  KEYBOARDTYPE=pc KEYTABLE=us rd_NO_DM rhgb quiet
    ...            initrd /initramfs-2.6.32-642.el6.x86_64.img
    ... title Red Hat Enterprise Linux 6 (2.6.32-642.el6.x86_64-2)
    ...            root (hd0,0)
    ...            kernel /vmlinuz-2.6.32-642.el6.x86_64 {kernel_boot_options} ro root=/dev/mapper/VolGroup-lv_root intel_iommu=on rd_NO_LUKS LANG=en_US.UTF-8 rd_NO_MD rd_LVM_LV=VolGroup/lv_swap SYSFONT=latarcyrheb-sun16 crashkernel=auto rd_LVM_LV=VolGroup/lv_root  KEYBOARDTYPE=pc KEYTABLE=us rd_NO_DM rhgb quiet
    ...            initrd /initramfs-2.6.32-642.el6.x86_64.img
    ... '''.strip()

    >>> config = Grub1Config(context_wrap(GRUB1_TEMPLATE))
    >>> shared = {Grub1Config: config}
    >>> result = GrubConf(None, shared)
    >>> grub_conf = shared[GrubConf]
    >>> grub_conf.kernel_initrds
    {'grub_initrds': [
        'initramfs-2.6.32-642.el6.x86_64.img',
        'initramfs-2.6.32-642.el6.x86_64.img'],
     'grub_kernels': [
        'vmlinuz-2.6.32-642.el6.x86_64',
        'vmlinuz-2.6.32-642.el6.x86_64']}
    >>> grub_conf.is_kdump_iommu_enabled
    False


    >>> GRUB2_TEMPLATE = '''
    ... set pager=1
    ... /
    ... menuentry 'Red Hat Enterprise Linux Workstation (3.10.0-327.36.3.el7.x86_64) 7.2 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-123.13.2.el7.x86_64-advanced-fbff9f50-62c3-484e-bca5-d53f672cda7c' {
    ...     load_video
    ...     set gfxpayload=keep
    ...     insmod gzio
    ...     insmod part_msdos
    ...     insmod ext2
    ...     set root='hd0,msdos1'
    ...     linux16 /vmlinuz-3.10.0-327.36.3.el7.x86_64 root=/dev/RHEL7CSB/Root ro rd.lvm.lv=RHEL7CSB/Root rd.luks.uuid=luks-96c66446-77fd-4431-9508-f6912bd84194 crashkernel=128M@16M rd.lvm.lv=RHEL7CSB/Swap vconsole.font=latarcyrheb-sun16 rhgb quiet LANG=en_GB.utf8
    ...     initrd16 /initramfs-3.10.0-327.36.3.el7.x86_64.img
    ... '''.strip()

    >>> config = Grub2Config(context_wrap(GRUB2_TEMPLATE))
    >>> shared = {Grub2Config: config}
    >>> result = GrubConf(None, shared)
    >>> result.kernel_initrds
    {'grub_initrds': [
        '/initramfs-3.10.0-327.36.3.el7.x86_64.img'],
     'grub_kernels': [
        '/vmlinuz-3.10.0-327.36.3.el7.x86_64']}
    >>> result.is_kdump_iommu_enabled
    False
"""

from falafel.core.plugins import reducer
from falafel.mappers.grub1_conf import Grub1Config
from falafel.mappers.grub2_conf import Grub2Config


@reducer(optional=[Grub1Config, Grub2Config], shared=True)
class GrubConf(object):
    """Process Grub configuration v1 or v2 based on which type is passed in

    Attributes:
        kernel_initrds (list)
        is_kdump_iommu_enabled (bool)

    Raises:
        Exeption: If shared is not Grub1Config pr Grub2Config
    """

    def __init__(self, local, shared):

        self.kernel_initrds = []
        self.crash_kernel_offset = ""
        self.is_kdump_iommu_enabled = False

        # get grub configuartion
        self.grub1 = shared.get(Grub1Config)
        self.grub2 = shared.get(Grub2Config)

        # grub1
        if (self.grub1):
            return self._get_grub1_info()

        # grub2
        elif (self.grub2):
            return self._get_grub2_info()

        raise Exception("Not Grub v1 or Grub v2.")

    def _get_grub1_info(self):
        """
        Process Grub v1 configuration file.
        """

        self.is_kdump_iommu_enabled = self.grub1.is_kdump_iommu_enabled
        self.kernel_initrds = self.grub1.kernels_initrds

    def _get_grub2_info(self):

        """
        Process Grub v2 configuration file.
        """

        self.is_kdump_iommu_enabled = False
        self.kernel_initrds = self.grub2.kernels_initrds
