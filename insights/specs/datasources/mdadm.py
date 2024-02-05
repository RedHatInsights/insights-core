"""
Custom datasources for mdadm information
"""
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import simple_command
# from insights.parsers.mdstat import Mdstat
from insights.specs import Specs


class LocalSpecs(Specs):
    """ Local specs used only by raid_devices datasource. """
    ls_dev_md = simple_command("ls /dev/")


@datasource(LocalSpecs.ls_dev_md, HostContext)
def raid_devices(broker):

    content = broker[LocalSpecs.ls_dev_md].content
    if content:
        if "No such file or directory" in content[0]:
            raise SkipComponent

        devices = []
        for line in content:
            for dev in line.split():
                if dev and dev.startswith("md") and dev != "md":
                    devices.append("/dev/" + dev)

        if devices:
            return devices

    raise SkipComponent


# @datasource(Mdstat, HostContext)
# def md_raid_arrays(broker):
#     """
#     Return the md RAID Array device names.

#     Sample data returned::

#         ["md1", "md2", "md3"]

#     Returns:
#         List[str]: Sorted list of md RAID Array device names.

#     Raises:
#         SkipComponent: Raised if no RAID Array name is available
#     """
#     md_raid_arrays = broker[Mdstat].mds.keys()
#     if md_raid_arrays:
#         return sorted(md_raid_arrays)
#     raise SkipComponent
