"""
Dracut module configuration files to build and extend the initramfs image
=========================================================================

This module contains the following parsers:

DracutModuleKdumpCaptureService - file ``/usr/lib/dracut/modules.d/99kdumpbase/kdump-capture.service``
------------------------------------------------------------------------------------------------------
"""

from insights.core import IniConfigFile
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.dracut_kdump_capture_service)
class DracutModuleKdumpCaptureService(IniConfigFile):
    """
    Class for parsing the `/usr/lib/dracut/modules.d/99kdumpbase/kdump-capture.service` file.

    .. note::
        Please refer to its super-class :py:class:`insights.core.IniConfigFile`
        for full usage.

    Sample input::

        [Unit]
        Description=Kdump Vmcore Save Service
        After=initrd.target initrd-parse-etc.service sysroot.mount
        Before=initrd-cleanup.service

        [Service]
        Type=oneshot
        ExecStart=/bin/kdump.sh
        StandardInput=null
        StandardOutput=syslog

    Examples:
        >>> type(config)
        <class 'insights.parsers.dracut_modules.DracutModuleKdumpCaptureService'>
        >>> 'Service' in config.sections()
        True
        >>> config.has_option('Service', 'Type')
        True
        >>> config.get('Service', 'Type') == 'oneshot'
        True
    """
    pass
