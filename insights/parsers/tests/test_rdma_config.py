from insights.parsers.rdma_config import RdmaConfig
from insights.tests import context_wrap

RDMA_CONFIG = """
# Load IPoIB
IPOIB_LOAD=yes
# Load SRP (SCSI Remote Protocol initiator support) module
SRP_LOAD=yes
# Load SRPT (SCSI Remote Protocol target support) module
SRPT_LOAD=yes
# Load iSER (iSCSI over RDMA initiator support) module
ISER_LOAD=yes
# Load iSERT (iSCSI over RDMA target support) module
ISERT_LOAD=yes
# Load RDS (Reliable Datagram Service) network protocol
RDS_LOAD=no
# Load NFSoRDMA client transport module
XPRTRDMA_LOAD=yes
# Load NFSoRDMA server transport module
SVCRDMA_LOAD=no
# Load Tech Preview device driver modules
TECH_PREVIEW_LOAD=no
# Should we modify the system mtrr registers?  We may need to do this if you
# get messages from the ib_ipath driver saying that it couldn't enable
# write combining for the PIO buffs on the card.
#
# Note: recent kernels should do this for us, but in case they don't, we'll
# leave this option
FIXUP_MTRR_REGS=no
"""


def test_rdma_config():
    rdma_config = RdmaConfig(context_wrap(RDMA_CONFIG)).data
    assert rdma_config["IPOIB_LOAD"] == 'yes'
    assert rdma_config["SRP_LOAD"] == 'yes'
    assert rdma_config["SVCRDMA_LOAD"] == 'no'
