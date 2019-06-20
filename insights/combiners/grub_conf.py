"""
GrubConf - The valid GRUB configuration
=======================================
Combiner for Red Hat Grub v1 and Grub v2 information.

This combiner uses the parsers:
:class:`insights.parsers.grub_conf.Grub1Config`,
:class:`insights.parsers.grub_conf.Grub1EFIConfig`,
:class:`insights.parsers.grub_conf.Grub2Config`,
:class:`insights.parsers.grub_conf.Grub2EFIConfig`,
:class:`insights.parsers.grub_conf.Grub2Grubenv`. and
:class:`insights.parsers.grub_conf.Grub2EFIGrubenv`.

It determines which parser was used by checking one of the follwing
parsers/combiners:
:class:`insights.parsers.installed_rpms.InstalledRpms`,
:class:`insights.parsers.cmdline.CmdLine`,
:class:`insights.parsers.ls_sys_firmware.LsSysFirmware`, and
:class:`insights.combiners.redhat_release.RedHatRelease`.


Examples:
    >>> type(grub_conf)
    <class 'insights.combiners.grub_conf.GrubConf'>
    >>> grub_conf.version
    2
    >>> grub_conf.is_efi
    False
    >>> grub_conf.kernel_initrds
    {'grub_initrds': ['/initramfs-3.10.0-327.36.3.el7.x86_64.img'],
     'grub_kernels': ['/vmlinuz-3.10.0-327.36.3.el7.x86_64']}
    >>> grub_conf.is_kdump_iommu_enabled
    False
    >>> grub_conf.get_grub_cmdlines('')
    []
"""

from insights.core.plugins import combiner
from insights.combiners.redhat_release import RedHatRelease
from insights.parsers.grub_conf import Grub1Config, Grub1EFIConfig
from insights.parsers.grub_conf import Grub2Config, Grub2EFIConfig
from insights.parsers.grub_conf import Grub2Grubenv, Grub2EFIGrubenv
from insights.parsers.ls_sys_firmware import LsSysFirmware
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.cmdline import CmdLine
from insights.parsers import ParseException


@combiner([Grub1Config, Grub2Config,
           Grub1EFIConfig, Grub2EFIConfig,
           Grub2Grubenv, Grub2EFIGrubenv],
          optional=[InstalledRpms, CmdLine, LsSysFirmware, RedHatRelease])
class GrubConf(object):
    """
    Process Grub configuration v1 or v2 based on which type is passed in.

    Raises:
        ParseException: when cannot find any valid grub configuration for the
                        booted system.

    Attributes:
        version (int): returns 1 or 2, version of the GRUB configuration
        is_efi (bool): returns True if the host is boot with EFI
        kernel_initrds (dict): returns a dict of the `kernel` and `initrd`
            files referenced in GRUB configuration files
        is_kdump_iommu_enabled (bool): returns true if any kernel entry
            contains "intel_iommu=on"
    """

    def __init__(self, grub1, grub2, grub1_efi, grub2_efi, grubenv, grubenv_efi,
                 rpms, cmdline, sys_firmware, rh_rel):

        self.version = self.is_kdump_iommu_enabled = None
        self.grub = self.kernel_initrds = None
        _grubs = list(filter(None, [grub1, grub2, grub1_efi, grub2_efi, grubenv, grubenv_efi]))
        # Check if `/sys/firmware/efi` exist?
        self.is_efi = '/sys/firmware/efi' in sys_firmware if sys_firmware else False

        if len(_grubs) == 1:
            self.grub = _grubs[0]
            self.is_efi = self.is_efi if sys_firmware else self.grub._efi
        else:
            _grub1, _grub2, _grubenv = (grub1_efi, grub2_efi, grubenv_efi) if self.is_efi else (grub1, grub2, grubenv)
            if rh_rel and rh_rel.rhel8:
                self.grub = _grubenv
            # Check grub version via installed-rpms
            else:
                if rpms:
                    # grub1
                    if 'grub2' not in rpms and 'grub' in rpms and _grub1 is not None:
                        self.grub = _grub1
                    # grub2
                    if 'grub' not in rpms and 'grub2' in rpms and _grub2 is not None:
                        self.grub = _grub2
                # Check grub version via the booted CmdLine
                if self.grub is None and cmdline:
                    # grub1
                    if "BOOT_IMAGE" not in cmdline or 'rd_LVM_LV' in cmdline:
                        self.grub = _grub1
                    # grub2
                    if "BOOT_IMAGE" in cmdline or 'rd.lvm.lv' in cmdline:
                        self.grub = _grub2

        if self.grub:
            self.version = self.grub._version
            self.is_kdump_iommu_enabled = self.grub.is_kdump_iommu_enabled
            self.kernel_initrds = self.grub.kernel_initrds or {}
        else:
            raise ParseException('No valid grub configuration is found.')

    def get_grub_cmdlines(self, search_text=None):
        """
        Get the boot entries in which `cmdline` contains the `search_text`,
        return all the boot entries by default.

        Arguments:
            search_text(str): keyword to find in the `cmdline`, being set to
                None by default.

        Returns:
            A list of :class:`insights.parsers.grub_conf.BootEntry` objects for
            each boot entry in which the `cmdline` contains the `search_text`.
        """
        if search_text is None:
            return self.grub.boot_entries
        elif search_text:
            return [entry for entry in self.grub.boot_entries if search_text in entry.cmdline]
        return []
