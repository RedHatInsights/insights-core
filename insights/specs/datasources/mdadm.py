"""
Custom datasources for mdadm information
"""
import glob
import os
import stat

from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource


@datasource(HostContext)
def raid_devices(broker):
    """ Glob extent "/dev/md*" to pass to ``mdadm_D`` Spec. """
    try:
        extended = glob.glob("/dev/md*")
        devices = [x for x in extended if stat.S_ISBLK(os.stat(x).st_mode)]
        if devices:
            return ' '.join(devices)
        else:
            raise SkipComponent("No /dev/md* raid devices found")
    except Exception as e:
        raise SkipComponent("Skipping raid_devices: {0}".format(str(e)))
