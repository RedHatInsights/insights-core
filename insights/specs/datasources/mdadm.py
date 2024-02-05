"""
Custom datasources for mdadm information
"""
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import simple_command
from insights.specs import Specs


class LocalSpecs(Specs):
    """ Local specs used only by raid_devices datasource. """
    ls_dev_md = simple_command("ls /dev/md*")


@datasource(LocalSpecs.ls_dev_md, HostContext)
def raid_devices(broker):

    content = broker[LocalSpecs.ls_dev_md].content
    print(content)
    if content:
        if "No such file or directory" in content[0]:
            raise SkipComponent

        devices = []
        for line in content:
            for dev in line.split():
                if dev and dev.startswith("/dev/md"):
                    devices.append(dev)

        if devices:
            return ' '.join(devices)

    raise SkipComponent
