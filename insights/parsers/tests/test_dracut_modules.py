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


def test_dracut_kdump_capture():
    kdump_service_conf = DracutModuleKdumpCaptureService(context_wrap(KDUMP_CAPTURE_SERVICE))
    assert 'Unit' in kdump_service_conf.sections()
    assert 'dracut-initqueue.service' in kdump_service_conf.get('Unit', 'After')


def test_doc():
    failed_count, tests = doctest.testmod(
        dracut_modules,
        globs={
            'config': dracut_modules.DracutModuleKdumpCaptureService(context_wrap(KDUMP_CAPTURE_SERVICE)),
        }
    )
    assert failed_count == 0
