"""
Combiner for GRUB v1 and v2 configurations
==========================================

Combiner for Red Hat Grub v1 and Grub v2 information.
This combiner uses both the Grub1Config and the Grub2Config parsers.
It determines which parser was used by checking the class attribute in shared.
When the appropriate Grub parser class is determined it executes the combiner
method for that class.
Successful completion of the combiner yields the following information

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
    >>> grub_conf = shared[GrubConf]
    >>> grub_conf.version
    1
    >>> grub_conf.kernel_initrds
    {'grub_initrds': [
        'initramfs-2.6.32-642.el6.x86_64.img',
        'initramfs-2.6.32-642.el6.x86_64.img'],
     'grub_kernels': [
        'vmlinuz-2.6.32-642.el6.x86_64',
        'vmlinuz-2.6.32-642.el6.x86_64']}
    >>> grub_conf.is_kdump_iommu_enabled
    False
    >>> grub_conf.get_grub_cmdlines('vmlinuz')[0].name
    'Red Hat Enterprise Linux 6 (2.6.32-642.el6.x86_64)'
    >>> grub_conf.get_grub_cmdlines()[1].name
    'Red Hat Enterprise Linux 6 (2.6.32-642.el6.x86_64-2)'



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
    >>> grub_conf = shared[GrubConf]
    >>> grub_conf.is_efi
    False
    >>> grub_conf.kernel_initrds
    {'grub_initrds': [
        '/initramfs-3.10.0-327.36.3.el7.x86_64.img'],
     'grub_kernels': [
        '/vmlinuz-3.10.0-327.36.3.el7.x86_64']}
    >>> grub_conf.is_kdump_iommu_enabled
    False
    >>> grub_conf.get_grub_cmdlines('')
    []
"""

from .. import defaults
from insights.core.plugins import combiner
from insights.parsers.grub_conf import Grub1Config, Grub1EFIConfig, Grub2Config, Grub2EFIConfig


@combiner([Grub1Config, Grub2Config, Grub2EFIConfig, Grub1EFIConfig])
class GrubConf(object):
    """Process Grub configuration v1 or v2 based on which type is passed in

    Attributes:
        version (int): returns 1 or 2, version of the GRUB configuration
        is_efi (bool): returns true if grub configuration for EFI-based system
        kernel_initrds (dict): returns a dict of the `kernel` and `initrd`
            files referenced in GRUB configuration files
        is_kdump_iommu_enabled (bool): returns true if any kernel entry
            contains "intel_iommu=on"

    """

    def __init__(self, grub1, grub2, grub2_efi, grub1_efi):

        self.version = self.is_efi = self.is_kdump_iommu_enabled = None
        self.grub = self.kernel_initrds = None
        # get grub configuration
        self.grub = grub1 or grub2 or grub2_efi or grub1_efi

        if self.grub:
            self.version = self.grub._version
            self.is_efi = self.grub._efi
            self.is_kdump_iommu_enabled = self.grub.is_kdump_iommu_enabled
            self.kernel_initrds = self.grub.kernel_initrds

    @defaults([])
    def get_grub_cmdlines(self, search_text=None):
        """
        Get the boot entries in which `cmdline` contains the `search_text`,
        return all the boot entries by default.

        Arguments:
            search_text(str): keyword to find in the `cmdline`, being set to
                None by default.

        Returns:
            A list of AttributeDict objects for each boot entry in which the
                `cmdline` contains the `search_text`. The AttributeDict boot
                entry looks like:

                - 'name': "Red Hat Enterprise Linux Server"
                - 'cmdline': "kernel /vmlinuz-2.6.32-431.11.2.el6.x86_64 rhgb quiet"
        """
        if search_text is None:
            return [entry for entry in self.grub.boot_entries]
        elif search_text:
            return [entry for entry in self.grub.boot_entries if search_text in entry.cmdline]
        return []
