"""
Libvirtd Logs
=============

This module contains the following parsers:

LibVirtdLog - file ``/var/log/libvirt/libvirtd.log``
----------------------------------------------------
LibVirtdQemuLog - file ``/var/log/libvirt/qemu/*.log``
------------------------------------------------------
"""
from insights.specs import Specs
from insights import LogFileOutput, parser


@parser(Specs.libvirtd_log)
class LibVirtdLog(LogFileOutput):
    """
    Parse the ``/var/log/libvirt/libvirtd.log`` log file.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput`

    Sample input::

        2013-10-23 17:32:19.909+0000: 14069: debug : do_open:1174 : trying driver 0 (Test) ...
        2013-10-23 17:32:19.909+0000: 14069: debug : do_open:1180 : driver 0 Test returned DECLINED
        2013-10-23 17:32:19.909+0000: 14069: debug : do_open:1174 : trying driver 1 (ESX) ...
        2013-10-23 17:32:19.909+0000: 14069: debug : do_open:1180 : driver 1 ESX returned DECLINED
        2013-10-23 17:32:19.909+0000: 14069: debug : do_open:1174 : trying driver 2 (remote) ...
        2013-10-23 17:32:19.957+0000: 14069: error : virNetTLSContextCheckCertDN:418 : Certificate [session] owner does not match the hostname AA.BB.CC.DD <============= IP Address
        2013-10-23 17:32:19.957+0000: 14069: warning : virNetTLSContextCheckCertificate:1102 : Certificate check failed Certificate [session] owner does not match the hostname AA.BB.CC.DD
        2013-10-23 17:32:19.957+0000: 14069: error : virNetTLSContextCheckCertificate:1105 : authentication failed: Failed to verify peer's certificate

    Examples:

        >>> "Certificate check failed Certificate" in libvirtd_log
        True
        >>> len(libvirtd_log.lines) # All lines, before filtering
        8
        >>> len(libvirtd_log.get('NetTLSContext')) # After filtering
        3
    """
    pass


@parser(Specs.libvirtd_qemu_log)
class LibVirtdQemuLog(LogFileOutput):
    """
        Parse the ``/var/log/libvirt/qemu/*.log`` log file.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput`

    Sample input from file /var/log/libvirt/qemu/bb912729-fa51-443b-bac6-bf4c795f081d.log::

        2019-06-04 05:33:22.280743Z qemu-kvm: -vnc 10.xxx.xxx.xxx:0: Failed to start VNC server: Failed to bind socket: Cannot assign requested address
        2019-06-04 05:33:2.285+0000: shutting down

    Examples:

        >>> from datetime import datetime
        >>> "shutting down" in libvirtd_qemu_log
        True
        >>> len(list(libvirtd_qemu_log.get_after(datetime(2019, 4, 26, 6, 55, 20))))
        2
        >>> libvirtd_qemu_log.file_name.strip('.log')  # Instance UUID
        'bb912729-fa51-443b-bac6-bf4c795f081d'
    """
    pass
