import doctest

from insights.tests import context_wrap
from insights.parsers import dracut_modules
from insights.parsers.dracut_modules import DracutModuleKdumpCaptureService

KDUMP_CAPTURE_SERVICE = """
[Unit]
Description=Kdump Vmcore Save Service
After=dracut-initqueue.service dracut-pre-mount.service dracut-mount.service dracut-pre-pivot.service
Before=initrd-cleanup.service
ConditionPathExists=/etc/initrd-release
OnFailure=emergency.target
OnFailureIsolate=yes

[Service]
Environment=DRACUT_SYSTEMD=1
Environment=NEWROOT=/sysroot
Type=oneshot
ExecStart=/bin/kdump.sh
StandardInput=null
StandardOutput=syslog
StandardError=syslog+console
KillMode=process
RemainAfterExit=yes

# Bash ignores SIGTERM, so we send SIGHUP instead, to ensure that bash
# terminates cleanly.
KillSignal=SIGHUP
""".strip()

MULTIPATHD_SAMPLE = """
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
""".strip()


def test_dracut_kdump_capture():
    kdump_service_conf = DracutModuleKdumpCaptureService(context_wrap(KDUMP_CAPTURE_SERVICE))
    assert 'Unit' in kdump_service_conf.sections()
    assert 'dracut-initqueue.service' in kdump_service_conf.get('Unit', 'After')


def test_dracut_multipathd_service():
    multipathd_service_conf = dracut_modules.DracutModuleMultipathdService(context_wrap(MULTIPATHD_SAMPLE))
    assert 'Unit' in multipathd_service_conf.sections()
    assert 'shutdown.target' in multipathd_service_conf.get('Unit', 'Conflicts')


def test_doc():
    failed_count, tests = doctest.testmod(
        dracut_modules,
        globs={
            'config': dracut_modules.DracutModuleKdumpCaptureService(context_wrap(KDUMP_CAPTURE_SERVICE)),
            'mp_service': dracut_modules.DracutModuleMultipathdService(context_wrap(MULTIPATHD_SAMPLE)),
        }
    )
    assert failed_count == 0
