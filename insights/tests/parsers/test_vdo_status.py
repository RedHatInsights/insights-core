import doctest
import pytest

from insights.core.exceptions import ParseException
from insights.core.plugins import ContentException
from insights.parsers import vdo_status
from insights.parsers.vdo_status import VDOStatus
from insights.tests import context_wrap


INPUT_EXP = """
VDO status 2019-07-27 04:40:40-04:00
rdma-qe-04.lab.bos.redhat.com
""".strip()


INPUT_SIMPLE_EXP = """
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
V??DOs:
  vdo1:
     XX: XX
  vdo2:
     XX: XX

"""

INPUT_STATUS_2 = """
VDO status:
  Date: '2019-09-23 02:00:38+02:00'
  Node: hello_test
Kernel module:
  Loaded: false
  Name: kvdo
  Version information:
    kvdo version: 6.1.2.41
Configuration:
  File: /etc/vdoconf.yml
  Last modified: '2018-06-13 16:46:03'
VDOs:
  vdoapp1:
    Acknowledgement threads: 1
    Activate: enabled
    Bio rotation interval: 64
    Bio submission threads: 4
    Block map cache size: 128M
    Block map period: 16380
    Block size: 4096
    CPU-work threads: 2
    Compression: enabled
    Configured write policy: auto
    Deduplication: enabled
    Device mapper status: not available
    Emulate 512 byte: disabled
    Hash zone threads: 1
    Index checkpoint frequency: 0
    Index memory setting: 0.25
    Index parallel factor: 0
    Index sparse: disabled
    Index status: not available
    Logical size: 466771896K
    Logical threads: 1
    Physical size: 450G
    Physical threads: 1
    Read cache: disabled
    Read cache size: 0M
    Slab size: 2G
    Storage device: /dev/sdh
    VDO statistics: not available
  vdoapp2:
    Acknowledgement threads: 1
    Activate: enabled
    Bio rotation interval: 64
    Bio submission threads: 4
    Block map cache size: 128M
    Block map period: 16380
    Block size: 4096
    CPU-work threads: 2
    Compression: enabled
    Configured write policy: auto
    Deduplication: enabled
    Device mapper status: not available
    Emulate 512 byte: disabled
    Hash zone threads: 1
    Index checkpoint frequency: 0
    Index memory setting: 0.25
    Index parallel factor: 0
    Index sparse: disabled
    Index status: not available
    Logical size: 466771896K
    Logical threads: 1
    Physical size: 450G
    Physical threads: 1
    Read cache: disabled
    Read cache size: 0M
    Slab size: 2G
    Storage device: /dev/sdc
    VDO statistics: not available
"""

INPUT_STATUS_SIMPLE = """
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
    Slab size: 2G
    VDO statistics:
      /dev/mapper/vdo1:
        block size: 4096
        data blocks used: 161863
        logical blocks: 844568
        logical blocks used: 844502
        overhead blocks used: 728175
        physical blocks: 1572864
        slab count: 26
  vdo2:
    Acknowledgement threads: 1
    Activate: enabled
    Slab size: 128M
    VDO statistics:
      /dev/mapper/vdo2:
        block size: 4096
        data blocks used: 161861
        logical blocks: 844562
        logical blocks used: 0
        overhead blocks used: 728172
        physical blocks: 1572861
        slab count: 26
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


INPUT_STATUS_FULL = """
VDO status:
  Date: '2019-07-24 20:48:16-04:00'
  Node: dell-m620-10.rhts.gsslab.pek2.redhat.com
Kernel module:
  Loaded: true
  Name: kvdo
  Version information:
    kvdo version: 6.1.0.153
Configuration:
  File: /etc/vdoconf.yml
  Last modified: '2019-07-24 20:47:59'
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
    Configured write policy: auto
    Deduplication: enabled
    Device mapper status: 0 8370216 vdo /dev/sda3 albserver online cpu=2,bio=4,ack=1,bioRotationInterval=64
    Emulate 512 byte: disabled
    Hash zone threads: 1
    Index checkpoint frequency: 0
    Index memory setting: 0.25
    Index parallel factor: 0
    Index sparse: disabled
    Index status: online
    Logical size: 4185108K
    Logical threads: 1
    Physical size: 7G
    Physical threads: 1
    Read cache: disabled
    Read cache size: 0M
    Slab size: 2G
    Storage device: /dev/sda3
    VDO statistics:
      /dev/mapper/vdo1:
        1K-blocks: 7340032
        1K-blocks available: 4191472
        1K-blocks used: 3148560
        512 byte emulation: false
        KVDO module bios used: 74572
        KVDO module bytes used: 851421880
        KVDO module peak bio count: 74860
        KVDO module peak bytes used: 851423752
        bios acknowledged discard: 0
        bios acknowledged flush: 0
        bios acknowledged fua: 0
        bios acknowledged partial discard: 0
        bios acknowledged partial flush: 0
        bios acknowledged partial fua: 0
        bios acknowledged partial read: 0
        bios acknowledged partial write: 0
        bios acknowledged read: 261
        bios acknowledged write: 0
        bios in discard: 0
        bios in flush: 0
        bios in fua: 0
        bios in partial discard: 0
        bios in partial flush: 0
        bios in partial fua: 0
        bios in partial read: 0
        bios in partial write: 0
        bios in progress discard: 0
        bios in progress flush: 0
        bios in progress fua: 0
        bios in progress read: 0
        bios in progress write: 0
        bios in read: 261
        bios in write: 0
        bios journal completed discard: 0
        bios journal completed flush: 0
        bios journal completed fua: 0
        bios journal completed read: 0
        bios journal completed write: 0
        bios journal discard: 0
        bios journal flush: 0
        bios journal fua: 0
        bios journal read: 0
        bios journal write: 0
        bios meta completed discard: 0
        bios meta completed flush: 0
        bios meta completed fua: 0
        bios meta completed read: 3
        bios meta completed write: 65
        bios meta discard: 0
        bios meta flush: 1
        bios meta fua: 1
        bios meta read: 3
        bios meta write: 65
        bios out completed discard: 0
        bios out completed flush: 0
        bios out completed fua: 0
        bios out completed read: 0
        bios out completed write: 0
        bios out discard: 0
        bios out flush: 0
        bios out fua: 0
        bios out read: 0
        bios out write: 0
        bios page cache completed discard: 0
        bios page cache completed flush: 0
        bios page cache completed fua: 0
        bios page cache completed read: 0
        bios page cache completed write: 0
        bios page cache discard: 0
        bios page cache flush: 0
        bios page cache fua: 0
        bios page cache read: 0
        bios page cache write: 0
        block map cache pressure: 0
        block map cache size: 134217728
        block map clean pages: 0
        block map dirty pages: 0
        block map discard required: 0
        block map failed pages: 0
        block map failed reads: 0
        block map failed writes: 0
        block map fetch required: 0
        block map flush count: 0
        block map found in cache: 0
        block map free pages: 32768
        block map incoming pages: 0
        block map outgoing pages: 0
        block map pages loaded: 0
        block map pages saved: 0
        block map read count: 0
        block map read outgoing: 0
        block map reclaimed: 0
        block map wait for page: 0
        block map write count: 0
        block size: 4096
        completed recovery count: 0
        compressed blocks written: 0
        compressed fragments in packer: 0
        compressed fragments written: 0
        current VDO IO requests in progress: 0
        current dedupe queries: 0
        data blocks used: 0
        dedupe advice stale: 0
        dedupe advice timeouts: 0
        dedupe advice valid: 0
        entries indexed: 0
        flush out: 0
        instance: 0
        invalid advice PBN count: 0
        journal blocks batching: 0
        journal blocks committed: 0
        journal blocks started: 0
        journal blocks writing: 0
        journal blocks written: 0
        journal commits requested count: 0
        journal disk full count: 0
        journal entries batching: 0
        journal entries committed: 0
        journal entries started: 0
        journal entries writing: 0
        journal entries written: 0
        logical blocks: 1046277
        logical blocks used: 0
        maximum VDO IO requests in progress: 9
        maximum dedupe queries: 0
        no space error count: 0
        operating mode: normal
        overhead blocks used: 787140
        physical blocks: 1835008
        posts found: 0
        posts not found: 0
        queries found: 0
        queries not found: 0
        read cache accesses: 0
        read cache data hits: 0
        read cache hits: 0
        read only error count: 0
        read-only recovery count: 0
        recovery progress (%): N/A
        reference blocks written: 0
        release version: 131337
        saving percent: N/A
        slab count: 2
        slab journal blocked count: 0
        slab journal blocks written: 0
        slab journal disk full count: 0
        slab journal flush count: 0
        slab journal tail busy count: 0
        slab summary blocks written: 0
        slabs opened: 0
        slabs reopened: 0
        updates found: 0
        updates not found: 0
        used percent: 42
        version: 26
        write amplification ratio: 0.0
        write policy: sync
  vdo2:
    Acknowledgement threads: 1
    Activate: enabled
    Bio rotation interval: 64
    Bio submission threads: 4
    Block map cache size: 128M
    Block map period: 16380
    Block size: 4096
    CPU-work threads: 2
    Compression: enabled
    Configured write policy: auto
    Deduplication: enabled
    Device mapper status: 0 4183912 vdo /dev/sda5 albserver online cpu=2,bio=4,ack=1,bioRotationInterval=64
    Emulate 512 byte: disabled
    Hash zone threads: 1
    Index checkpoint frequency: 0
    Index memory setting: 0.25
    Index parallel factor: 0
    Index sparse: disabled
    Index status: online
    Logical size: 2091956K
    Logical threads: 1
    Physical size: 5G
    Physical threads: 1
    Read cache: disabled
    Read cache size: 0M
    Slab size: 2G
    Storage device: /dev/sda5
    VDO statistics:
      /dev/mapper/vdo2:
        1K-blocks: 5242880
        1K-blocks available: 2095736
        1K-blocks used: 3147144
        512 byte emulation: false
        KVDO module bios used: 74572
        KVDO module bytes used: 851421880
        KVDO module peak bio count: 74860
        KVDO module peak bytes used: 851423752
        bios acknowledged discard: 0
        bios acknowledged flush: 0
        bios acknowledged fua: 0
        bios acknowledged partial discard: 0
        bios acknowledged partial flush: 0
        bios acknowledged partial fua: 0
        bios acknowledged partial read: 0
        bios acknowledged partial write: 0
        bios acknowledged read: 265
        bios acknowledged write: 0
        bios in discard: 0
        bios in flush: 0
        bios in fua: 0
        bios in partial discard: 0
        bios in partial flush: 0
        bios in partial fua: 0
        bios in partial read: 0
        bios in partial write: 0
        bios in progress discard: 0
        bios in progress flush: 0
        bios in progress fua: 0
        bios in progress read: 0
        bios in progress write: 0
        bios in read: 265
        bios in write: 0
        bios journal completed discard: 0
        bios journal completed flush: 0
        bios journal completed fua: 0
        bios journal completed read: 0
        bios journal completed write: 0
        bios journal discard: 0
        bios journal flush: 0
        bios journal fua: 0
        bios journal read: 0
        bios journal write: 0
        bios meta completed discard: 0
        bios meta completed flush: 0
        bios meta completed fua: 0
        bios meta completed read: 4
        bios meta completed write: 65
        bios meta discard: 0
        bios meta flush: 1
        bios meta fua: 1
        bios meta read: 4
        bios meta write: 65
        bios out completed discard: 0
        bios out completed flush: 0
        bios out completed fua: 0
        bios out completed read: 0
        bios out completed write: 0
        bios out discard: 0
        bios out flush: 0
        bios out fua: 0
        bios out read: 0
        bios out write: 0
        bios page cache completed discard: 0
        bios page cache completed flush: 0
        bios page cache completed fua: 0
        bios page cache completed read: 0
        bios page cache completed write: 0
        bios page cache discard: 0
        bios page cache flush: 0
        bios page cache fua: 0
        bios page cache read: 0
        bios page cache write: 0
        block map cache pressure: 0
        block map cache size: 134217728
        block map clean pages: 0
        block map dirty pages: 0
        block map discard required: 0
        block map failed pages: 0
        block map failed reads: 0
        block map failed writes: 0
        block map fetch required: 0
        block map flush count: 0
        block map found in cache: 0
        block map free pages: 32768
        block map incoming pages: 0
        block map outgoing pages: 0
        block map pages loaded: 0
        block map pages saved: 0
        block map read count: 0
        block map read outgoing: 0
        block map reclaimed: 0
        block map wait for page: 0
        block map write count: 0
        block size: 4096
        completed recovery count: 0
        compressed blocks written: 0
        compressed fragments in packer: 0
        compressed fragments written: 0
        current VDO IO requests in progress: 0
        current dedupe queries: 0
        data blocks used: 1
        dedupe advice stale: 0
        dedupe advice timeouts: 0
        dedupe advice valid: 0
        entries indexed: 0
        flush out: 0
        instance: 1
        invalid advice PBN count: 0
        journal blocks batching: 0
        journal blocks committed: 0
        journal blocks started: 0
        journal blocks writing: 0
        journal blocks written: 0
        journal commits requested count: 0
        journal disk full count: 0
        journal entries batching: 0
        journal entries committed: 0
        journal entries started: 0
        journal entries writing: 0
        journal entries written: 0
        logical blocks: 522989
        logical blocks used: 3
        maximum VDO IO requests in progress: 7
        maximum dedupe queries: 0
        no space error count: 0
        operating mode: normal
        overhead blocks used: 786786
        physical blocks: 1310720
        posts found: 0
        posts not found: 0
        queries found: 0
        queries not found: 0
        read cache accesses: 0
        read cache data hits: 0
        read cache hits: 0
        read only error count: 0
        read-only recovery count: 0
        recovery progress (%): N/A
        reference blocks written: 0
        release version: 131337
        saving percent: N/A
        slab count: 1
        slab journal blocked count: 0
        slab journal blocks written: 0
        slab journal disk full count: 0
        slab journal flush count: 0
        slab journal tail busy count: 0
        slab summary blocks written: 0
        slabs opened: 0
        slabs reopened: 0
        updates found: 0
        updates not found: 0
        used percent: 60
        version: 26
        write amplification ratio: 0.0
        write policy: sync
""".strip()

VDO_STATUS_NO_COMMAND = """
-bash: /usr/bin/vdo: No such file or directory
""".strip()


def test_vdo_status2():
    vdo = VDOStatus(context_wrap(INPUT_STATUS_2))
    assert vdo.data['VDOs']['vdoapp1']['VDO statistics'] == 'not available'


def test_vdo_status_exp2_0():
    """
    Here test the examples cause expections
    """
    with pytest.raises(ParseException) as sc1:
        vdo = VDOStatus(context_wrap(INPUT_STATUS_2))
        vdo.get_physical_blocks_of_vol('vdoapp1')
    assert "Not available device mapper path in" in str(sc1)


def test_vdo_status_exp2_1():
    """
    Here test the examples cause expections
    """
    with pytest.raises(KeyError) as sc1:
        vdo = VDOStatus(context_wrap(INPUT_STATUS_2))
        vdo.get_physical_blocks_of_vol('vdoapp999')
    assert "No key(s) named:" in str(sc1)


def test_vdo_status_simple():
    vdo = VDOStatus(context_wrap(INPUT_STATUS_SIMPLE))
    assert vdo.data['VDO status'] == {'Date': '2019-07-27 04:40:40-04:00', 'Node': 'rdma-qe-04.lab.bos.redhat.com'}
    assert vdo.data['VDOs']['vdo1']['Activate'] == 'enabled'
    assert vdo.data['VDO status']['Date'] == '2019-07-27 04:40:40-04:00'
    assert vdo.data['VDO status']['Node'] == 'rdma-qe-04.lab.bos.redhat.com'

    assert vdo.get_slab_size_of_vol('vdo1') == '2G'
    assert vdo.volumns == ['vdo1', 'vdo2']

    assert vdo.get_physical_blocks_of_vol('vdo1') == 1572864
    assert vdo.get_overhead_used_of_vol('vdo1') == 728175
    assert vdo.get_physical_used_of_vol('vdo1') == 161863
    assert vdo.get_physical_free_of_vol('vdo1') == 682826

    assert vdo.get_logical_blocks_of_vol('vdo1') == 844568
    assert vdo.get_logical_used_of_vol('vdo1') == 844502
    assert vdo.get_logical_free_of_vol('vdo1') == 66


def test_vdo_status_empty():
    vdo = VDOStatus(context_wrap(INPUT_EMPTY))
    assert vdo.data["VDOs"] == {}

    assert vdo.data["Configuration"]["File"] == "does not exist"
    assert vdo.data["Configuration"]["Last modified"] == "not available"


def test_vdo_status_full():
    vdo = VDOStatus(context_wrap(INPUT_STATUS_FULL))
    assert vdo.data["VDO status"]["Date"] == "2019-07-24 20:48:16-04:00"
    assert vdo.data["VDO status"]["Node"] == "dell-m620-10.rhts.gsslab.pek2.redhat.com"

    assert vdo.data["Kernel module"]["Name"] == "kvdo"
    assert vdo.data["Kernel module"]["Version information"]["kvdo version"] == "6.1.0.153"

    assert vdo.data["Configuration"]["File"] == "/etc/vdoconf.yml"
    assert vdo.data["Configuration"]["Last modified"] == "2019-07-24 20:47:59"

    assert vdo.data["VDOs"]["vdo1"]["Acknowledgement threads"] == 1
    assert vdo.data["VDOs"]["vdo1"]["Device mapper status"] == "0 8370216 vdo /dev/sda3 albserver online cpu=2,bio=4,ack=1,bioRotationInterval=64"
    assert vdo.data["VDOs"]["vdo1"]["VDO statistics"]["/dev/mapper/vdo1"]["KVDO module bios used"] == 74572

    assert vdo.get_slab_size_of_vol('vdo1') == '2G'

    assert vdo.volumns == ['vdo1', 'vdo2']

    assert vdo.get_physical_blocks_of_vol('vdo1') == 1835008
    assert vdo.get_overhead_used_of_vol('vdo1') == 787140
    assert vdo.get_physical_used_of_vol('vdo1') == 0

    assert vdo.get_logical_blocks_of_vol('vdo1') == 1046277
    assert vdo.get_logical_used_of_vol('vdo1') == 0

    assert vdo.get_logical_free_of_vol('vdo1') == 1046277
    assert vdo.get_physical_free_of_vol('vdo1') == 1047868

    assert vdo.get_logical_used_of_vol('vdo2') == 3
    assert vdo.get_physical_used_of_vol('vdo2') == 1


def test_vdo_status_documentation():
    """
    Here we test the examples in the documentation automatically using
    doctest.  We set up an environment which is similar to what a rule
    writer might see - a '/usr/bin/vdo status' command output that has
    been passed in as a parameter to the rule declaration.
    """
    env = {'vdo': VDOStatus(context_wrap(INPUT_STATUS_FULL))}
    failed, total = doctest.testmod(vdo_status, globs=env)
    assert failed == 0


def test_vdo_status_exp():
    """
    Here test the examples cause expections
    """
    with pytest.raises(ParseException) as sc1:
        VDOStatus(context_wrap(INPUT_EXP))
    assert "couldn't parse yaml" in str(sc1)


def test_vdo_status_exp3():
    """
    Here test the examples cause expections
    """
    with pytest.raises(KeyError) as sc1:
        vdo = VDOStatus(context_wrap(INPUT_STATUS_SIMPLE))
        vdo.get_physical_blocks_of_vol('vdo3')
    assert "No key(s) named" in str(sc1)


def test_vdo_status_exp4():
    """
    Test for ContentException
    """
    with pytest.raises(ContentException) as ce:
        VDOStatus(context_wrap(VDO_STATUS_NO_COMMAND))
    assert "No such file or directory" in str(ce.value)
