from insights.parsers import SkipException
from insights.parsers import vdostats_verbose, vdo_status
from insights.parsers.vdo_status import VDOStatus
from insights.tests import context_wrap
import pytest
import doctest

INPUT_STATUS = """
VDO status:
  Date: '2019-07-27 04:40:40-04:00'
  Node: rdma-qe-04.lab.bos.redhat.com
Kernel module:
  Loaded: true
  Name: kvdo
  Version information:
    kvdo version: 6.1.0.153
Configuration:
  File: /etc/vdoconf.yml
  Last modified: '2019-07-26 05:07:48'
VDOs:
  vdo1:
    Acknowledgement threads: 1
    Activate: enabled
    Bio rotation interval: 64
    Bio submission threads: 4
    Block map cache size: 128M
    Block map period: 16380
    Block size: 4096
    CPU-work threads: 2
    Compression: enabled
"""

INPUT_EMPTY = """
VDO status:
  Date: '2019-07-25 01:38:47-04:00'
  Node: rdma-dev-09.lab.bos.redhat.com
Kernel module:
  Loaded: false
  Name: kvdo
  Version information:
    kvdo version: 6.1.0.153
Configuration:
  File: does not exist
  Last modified: not available
VDOs: {}
""".strip()


def test_vdo_status():
    vdo = VDOStatus(context_wrap(INPUT_STATUS))
    vdo = VDOStatus(context_wrap(INPUT_EMPTY))
    print(vdo.data)
    assert vdo.data["Driver"] == "bnx2x 1.712.30-0"
    assert vdo.data["Revision"] == "10"
    assert vdo.data["Manufacturer"] == "Broadcom Corporation"
    assert vdo.data["Serial Number"] == "2C44FD8F4418"
    assert vdo.data["Number of Ports"] == "1"


def test_vdo_status_documentation():
    """
    Here we test the examples in the documentation automatically using
    doctest.  We set up an environment which is similar to what a rule
    writer might see - a '/usr/bin/vdo status' command output that has
    been passed in as a parameter to the rule declaration.
    """
    env = {'vdo': VDOStatus(context_wrap(INPUT_STATUS))} 
    failed, total = doctest.testmod(vdo_status, globs=env)
    assert failed == 0

#def test_vdo_status_exp():
#    """
#    Here test the examples cause expections
#    """
#    with pytest.raises(SkipException) as sc1:
#        VDOStatus(context_wrap(""))
#    assert "Input content is empty" in str(sc1)
