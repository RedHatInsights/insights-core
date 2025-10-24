"""
Grubby
======
Combiner for command ``/usr/sbin/grubby`` parsers.

This combiner uses the parsers:
:class:`insights.parsers.grubby.GrubbyDefaultIndex`,
:class:`insights.parsers.grubby.GrubbyInfoAll`,
:class:`insights.parsers.grubenv.GrubEnv`.
"""

import re

from insights.core.exceptions import ParseException
from insights.core.filters import add_filter
from insights.core.plugins import combiner
from insights.parsers import parse_cmdline_args
from insights.parsers.grub_conf import BootEntry
from insights.parsers.grubby import GrubbyDefaultIndex, GrubbyInfoAll
from insights.parsers.grubenv import GrubEnv
from insights.parsers.ls import LSlanFiltered
from insights.parsers.ls_sys_firmware import LsSysFirmware
from insights.specs import Specs

add_filter(Specs.ls_lan_filtered_dirs, '/sys/firmware')
add_filter(Specs.ls_lan_filtered, ['/sys/firmware', 'efi'])


@combiner([LSlanFiltered, LsSysFirmware])
class IsUEFIBoot(object):
    """
    Tell if the host is boot with UEFI by computing on the files under
    /sys/firmware directory.

    Attributes:
        is_uefi_boot (bool): if the host is boot with UEFI

    Raises:
        ParseException: when failing on the computing of /sys/firmware file
    """

    def __init__(self, ls_lan, ls_sf):
        sf_dir = '/sys/firmware'
        sf_efi_dir = '/sys/firmware/efi'
        ls = ls_lan or ls_sf
        self.is_uefi_boot = (
            sf_efi_dir in ls or (sf_dir in ls and ls.dir_contains(sf_dir, 'efi')) if ls else False
        )

    def __bool__(self):
        return self.is_uefi_boot

    __nonzero__ = __bool__


@combiner(GrubbyInfoAll, GrubbyDefaultIndex, optional=[GrubEnv, IsUEFIBoot])
class Grubby(object):
    """
    Combine command "grubby" parsers into one Combiner.

    Attributes:
        boot_entries (list): All boot entries as ``BootEntry`` instances
        default_index (int): The numeric index of the default boot entry
        default_boot_entry (dict): The boot information for default kernel
        default_kernel (str): The path of the default kernel
        is_efi (bool): True if the host is boot with UEFI

    Raises:
        ParseException: when parsing into error.
    """

    def __init__(self, grubby_info_all, grubby_default_index, grubenv, is_uefi):

        self._boot_entries = {
            i: self._gen_boot_entry(e) for i, e in grubby_info_all.boot_entries.items()
        }
        self.default_index = grubby_default_index.default_index

        if self.default_index not in self._boot_entries:
            raise ParseException(
                "DEFAULT index %s not exist in parsed boot_entries: %s"
                % (self.default_index, list(self._boot_entries.keys()))
            )
        self.default_boot_entry = self._boot_entries[self.default_index]

        self.default_kernel = self.default_boot_entry.get("kernel")
        if not self.default_kernel:
            raise ParseException(
                "DEFAULT kernel-path not exist in default-index: %s" % self.default_index
            )

        self.version = self._version = 2  # GRUB2
        self.is_efi = bool(is_uefi)
        self._kernel_initrds = None  # lazy load
        self._is_kdump_iommu_enabled = None  # lazy load
        self._expand_with_grubenv(grubenv) if grubenv else None
        self.boot_entries = list(self._boot_entries[idx] for idx in sorted(self._boot_entries))

    def _gen_boot_entry(self, entry_data):
        new_entry_data = {
            'name': entry_data.get('title', ''),
            'cmdline': " ".join(
                [
                    entry_data.get('kernel', ''),
                    "root=%s" % entry_data["root"] if entry_data.get('root') else '',
                    entry_data.get('raw_args', ''),
                ]
            ).strip(),  # compatiable for GrubConf usage
        }
        new_entry_data.update(entry_data)
        if entry_data.get('root') and entry_data.get('args'):
            new_entry_data['args'] = parse_cmdline_args(new_entry_data['cmdline'])
            new_entry_data.pop('raw_args')
        return BootEntry(new_entry_data)

    def _expand_with_grubenv(self, grubenv):
        """
        If grubenv, expand the variables for boot_entries:
            - $kernelopts, $tuned_params, $tuned_initrd
        """
        for entry in self._boot_entries.values():
            if_reload_args = False
            if "$kernelopts" in entry.get('args', {}):
                entry['cmdline'] = re.sub(
                    "\\$kernelopts", grubenv.get("kernelopts", ""), entry['cmdline']
                ).strip()
                if_reload_args = True
            if "$tuned_params" in entry.get('args', {}):
                entry['cmdline'] = re.sub(
                    "\\$tuned_params", grubenv.get("tuned_params", ""), entry['cmdline']
                ).strip()
                if_reload_args = True
            if if_reload_args:
                entry['args'] = parse_cmdline_args(entry['cmdline'])

            if "$tuned_initrd" in entry.get('initrd', ''):
                entry['initrd'] = re.sub(
                    "\\$tuned_initrd", grubenv.get("tuned_initrd", ""), entry['initrd']
                ).strip()

    @property
    def kernel_initrds(self):
        """
        Get the `kernel` and `initrd` files referenced in GRUB2 boot entries

        Returns:
            dict: A dict of defined key `grub_kernels` and `grub_initrds`,
                with a list of `kernel` or `initrd` file names as value.

        .. note::
            This property is for the compatiable usage in combiner `GrubConf`.
            To tell the default kernel path or entry, use the provided
            attribute `default_kernel` or `default_boot_entry` directly.
        """
        if self._kernel_initrds is None:
            grub_kernels = []
            grub_initrds = []
            for entry in self._boot_entries.values():
                _kernel = entry.get('kernel', '')
                if _kernel and 'vmlinuz-' in _kernel:
                    entry_kernel = _kernel.split('vmlinuz-', 1)[-1]
                    grub_kernels.append('vmlinuz-' + entry_kernel) if entry_kernel else None

                _initrd = entry.get('initrd', '')
                split_key = 'initramfs-' if 'initramfs-' in _initrd else 'initrd-'
                if _initrd and split_key in _initrd:
                    entry_initrd = _initrd.split(split_key, 1)[-1]
                    grub_initrds.append(split_key + entry_initrd) if entry_initrd else None

            self._kernel_initrds = {"grub_kernels": grub_kernels, "grub_initrds": grub_initrds}

        return self._kernel_initrds

    @property
    def is_kdump_iommu_enabled(self):
        """
        Does any boot entry have 'intel_iommu=on' set in "cmdline"?

        Returns:
            bool: ``True`` when 'intel_iommu=on' is set, otherwise ``False``
        """
        if self._is_kdump_iommu_enabled is None:
            self._is_kdump_iommu_enabled = False
            for entry in self._boot_entries.values():
                if "intel_iommu=on" in entry.get('cmdline', ''):
                    self._is_kdump_iommu_enabled = True
                    break
        return self._is_kdump_iommu_enabled
