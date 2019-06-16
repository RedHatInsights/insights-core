#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import doctest
import pytest
from insights.tests import context_wrap
from insights.parsers import rdma_config as scc, SkipException

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

RDMA_CONFIG_INPUT_EMPTY = """
# Load IPoIB
#IPOIB_LOAD=yes
# Load SRP (SCSI Remote Protocol initiator support) module
#SRP_LOAD=yes
# Load SRPT (SCSI Remote Protocol target support) module
#SRPT_LOAD=yes
# Load iSER (iSCSI over RDMA initiator support) module
#ISER_LOAD=yes
# Load iSERT (iSCSI over RDMA target support) module
#ISERT_LOAD=yes
# Load RDS (Reliable Datagram Service) network protocol
#RDS_LOAD=no
# Load NFSoRDMA client transport module
#XPRTRDMA_LOAD=yes
# Load NFSoRDMA server transport module
#SVCRDMA_LOAD=no
# Load Tech Preview device driver modules
#TECH_PREVIEW_LOAD=no
# Should we modify the system mtrr registers?  We may need to do this if you
# get messages from the ib_ipath driver saying that it couldn't enable
# write combining for the PIO buffs on the card.
#
# Note: recent kernels should do this for us, but in case they don't, we'll
# leave this option
#FIXUP_MTRR_REGS=no
"""


def test_rdma_config():
    rdma_config = scc.RdmaConfig(context_wrap(RDMA_CONFIG))
    assert rdma_config["IPOIB_LOAD"] == 'yes'
    assert rdma_config["SRP_LOAD"] == 'yes'
    assert rdma_config["SVCRDMA_LOAD"] == 'no'


def test_rdma_config_empty():
    with pytest.raises(SkipException):
        scc.RdmaConfig(context_wrap(RDMA_CONFIG_INPUT_EMPTY))


def test_rdma_config_doc():
    env = {
            'rdma_conf': scc.RdmaConfig(context_wrap(RDMA_CONFIG)),
          }
    failed, total = doctest.testmod(scc, globs=env)
    assert failed == 0
