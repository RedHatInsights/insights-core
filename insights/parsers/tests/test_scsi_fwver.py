from insights.parsers.scsi_fwver import SCSIFWver
from insights.tests import context_wrap
from insights.util import keys_in

SCSI_HOST_PATH = "/sys/class/scsi_host/host0/fwrev"
SCSI_HOSTS = """
2.02X12 (U3H2.02X12), sli-3
""".strip()

def test_scsi_fwver():
    context = context_wrap(SCSI_HOSTS)
    context.path = SCSI_HOST_PATH
    r = SCSIFWver(context)
    r.scsi_host = 'host0'
