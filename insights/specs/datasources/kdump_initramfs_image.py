"""
Custom datasource to get the kdump initramfs image.
"""

from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.parsers.ls_boot import LsBoot


@datasource(LsBoot, HostContext)
def kdump_image(broker):
    """
    This datasource provides file name of the kdump initramfs image.

    Sample data returned::

        'initramfs-4.18.0-240.el8.x86_64kdump.img'

    Returns:
        String: The kdump initramfs image file.

    Raises:
        SkipComponent: When there is not any kdump initramfs image.
    """

    content = broker[LsBoot]
    if content:
        kdump_images = []
        boot_list = content.files_of('/boot')
        for file in boot_list:
            if file.endswith('kdump.img'):
                kdump_images.append('/boot/' + file)
        if kdump_images:
            return kdump_images

    raise SkipComponent
