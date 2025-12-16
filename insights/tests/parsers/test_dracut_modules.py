import doctest

from insights.tests import context_wrap
from insights.parsers import dracut_modules
from insights.parsers.dracut_modules import DracutModuleKdumpCaptureService, DracutOsslFilesConfig

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


def test_dracut_ossl_files_config_empty():
    """Test parser with empty output"""
    ossl_files = DracutOsslFilesConfig(context_wrap(""))
    assert ossl_files.has_error is False
    assert ossl_files.content == [""]


def test_dracut_ossl_files_config_error():
    """Test parser with error message"""
    error_output = "configuration file routines:def_load_bio:missing equal s"
    ossl_files = DracutOsslFilesConfig(context_wrap(error_output))
    assert ossl_files.has_error is True
    assert ossl_files.content == [error_output]


def test_dracut_ossl_files_config_multiple_lines():
    """Test parser with multiple lines including error message"""
    multiple_lines = """some other output line
configuration file routines:def_load_bio:missing equal s
another line of output"""
    ossl_files = DracutOsslFilesConfig(context_wrap(multiple_lines))
    assert ossl_files.has_error is True
    assert len(ossl_files.content) == 3


def test_dracut_ossl_files_config_no_error():
    """Test parser with multiple lines but no error message"""
    no_error = """some output line
another output line
normal configuration output"""
    ossl_files = DracutOsslFilesConfig(context_wrap(no_error))
    assert ossl_files.has_error is False
    assert len(ossl_files.content) == 3


def test_doc():
    failed_count, tests = doctest.testmod(
        dracut_modules,
        globs={
            'config': dracut_modules.DracutModuleKdumpCaptureService(context_wrap(KDUMP_CAPTURE_SERVICE)),
        }
    )
    assert failed_count == 0
