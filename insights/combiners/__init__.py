from insights.core.filters import add_filter
from insights.core.plugins import combiner
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
