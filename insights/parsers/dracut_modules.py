"""
Dracut module configuration files to build and extend the initramfs image
=========================================================================

This module contains the following parsers:

DracutModuleKdumpCaptureService - file ``/usr/lib/dracut/modules.d/99kdumpbase/kdump-capture.service``
------------------------------------------------------------------------------------------------------

DracutModuleMultipathdService - file ``/usr/lib/dracut/modules.d/90multipath/multipathd.service``
-------------------------------------------------------------------------------------------------

"""

from insights import parser, IniConfigFile
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
        >>> 'Service' in config.sections()
        True
        >>> config.has_option('Service', 'Type')
        True
        >>> config.get('Service', 'Type') == 'oneshot'
        True
    """
    pass


@parser(Specs.dracut_multipathd_service)
class DracutModuleMultipathdService(IniConfigFile):
    """
    Class for parsing the `/usr/lib/dracut/modules.d/90multipath/multipathd.service` file.

    .. note::
        Please refer to its super-class :py:class:`insights.core.IniConfigFile`
        for full usage.

    Sample input::

        [Unit]
        Description=Device-Mapper Multipath Device Controller
        Before=iscsi.service iscsid.service lvm2-activation-early.service
        Wants=systemd-udev-trigger.service systemd-udev-settle.service local-fs-pre.target
        After=systemd-udev-trigger.service systemd-udev-settle.service
        DefaultDependencies=no
        Conflicts=shutdown.target
        ConditionKernelCommandLine=!nompath

        [Service]
        Type=simple
        ExecStartPre=-/sbin/modprobe dm-multipath
        ExecStart=/sbin/multipathd -s -d
        ExecReload=/sbin/multipathd reconfigure
        ExecStop=/sbin/multipathd shutdown

        [Install]
        WantedBy=sysinit.target

    Examples:
        >>> 'Unit' in mp_service.sections()
        True
        >>> mp_service.has_option('Unit', 'DefaultDependencies')
        True
        >>> mp_service.get('Unit', 'DefaultDependencies') == 'no'
        True
    """
    pass
