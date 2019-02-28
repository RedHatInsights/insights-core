"""
RdmaConfig - file ``/etc/rdma/rdma.conf``
=========================================
"""
from .. import get_active_lines, Parser, parser, LegacyItemAccess
from insights.parsers import split_kv_pairs
from insights.specs import Specs
from insights.parsers import SkipException


@parser(Specs.rdma_conf)
class RdmaConfig(Parser, LegacyItemAccess):
    """
    This class will parse the output of file ``/etc/rdma/rdma.conf``.

    The rdma service reads /etc/rdma/rdma.conf file to find out which
    kernel-level and user-level RDMA protocols the administrator
    wants to be loaded by default.

    Attributes:
        data (dict): Dictionary of keys with values in dict.

    Sample configuration file::

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

    Examples:
        >>> rdma_conf['IPOIB_LOAD']
        'yes'
        >>> rdma_conf["SRP_LOAD"]
        'yes'
        >>> rdma_conf["SVCRDMA_LOAD"]
        'no'
    """

    def parse_content(self, content):
        _content = get_active_lines(content)
        if not _content:
            raise SkipException("Empty content.")

        self.data = split_kv_pairs(_content)
