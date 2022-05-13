import doctest
from insights.parsers import scsi_fwver
from insights.parsers.scsi_fwver import SCSIFWver
from insights.tests import context_wrap

SCSI_HOST0_PATH = "/sys/class/scsi_host/host0/fwrev"
SCSI_HOSTS_0 = """
2.02X12 (U3H2.02X12), sli-3
""".strip()

SCSI_HOST1_PATH = "/sys/class/scsi_host/host1/fwrev"
SCSI_HOSTS_1 = """
2.02X13 (U3H3.02X13), sli-3
""".strip()

SCSI_HOST2_PATH = "/sys/class/scsi_host/host2/fwrev"
SCSI_HOSTS_2 = """
2.02X11 (U3H1.02X11)
""".strip()


def test_scsi_fwver_host0():
    context = context_wrap(SCSI_HOSTS_0, SCSI_HOST0_PATH)
    r = SCSIFWver(context)
    assert r.scsi_host == 'host0'
    assert r.host_mode == ['2.02X12 (U3H2.02X12)', 'sli-3']
    assert r.data == {'host0': ['2.02X12 (U3H2.02X12)', 'sli-3']}


def test_scsi_fwver_host1():
    context = context_wrap(SCSI_HOSTS_1, SCSI_HOST1_PATH)
    r = SCSIFWver(context)
    assert r.scsi_host == 'host1'
    assert r.host_mode == ['2.02X13 (U3H3.02X13)', 'sli-3']
    assert r.data == {'host1': ['2.02X13 (U3H3.02X13)', 'sli-3']}


def test_scsi_fwver_host2():
    context = context_wrap(SCSI_HOSTS_2, SCSI_HOST2_PATH)
    r = SCSIFWver(context)
    assert r.scsi_host == 'host2'
    assert r.host_mode == ['2.02X11 (U3H1.02X11)']
    assert r.data == {'host2': ['2.02X11 (U3H1.02X11)']}


def test_scsi_fwver_doc_examples():
    env = {'scsi_obj': SCSIFWver(context_wrap(SCSI_HOSTS_0, SCSI_HOST0_PATH))}
    failed, total = doctest.testmod(scsi_fwver, globs=env)
    assert failed == 0
