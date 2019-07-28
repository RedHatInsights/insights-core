from insights.tests import context_wrap
from insights.parsers.vdo_status import VDOStatus
from insights.combiners import vdo_status_calculation
from insights.combiners.vdo_status_calculation import VDOStatusCalculation
from insights.parsers import ParseException
import pytest
import doctest


INPUT_FULL = """
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
        data blocks used: 23
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
        logical blocks used: 323
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

INPUT_EXP = """
VDO status 2019-07-27 04:40:40-04:00
rdma-qe-04.lab.bos.redhat.com
""".strip()


def test_values():
    pda = VDOStatus(context_wrap(INPUT_FULL))
    res = VDOStatusCalculation(pda)

    assert res.get_slab_size('vdo1') == '2G'
    assert res.slab_size == '2G'

    assert res.volumns == ['vdo2', 'vdo1']
    assert res.get_all_volumns() == ['vdo2', 'vdo1']

    assert res.get_physical_blocks('vdo1') == 1835008
    assert res.physical_size == 1835008

    assert res.overhead_used == 787140
    assert res.get_overhead_used('vdo1') == 787140

    assert res.get_physical_used_pct('vdo1') == 0.0

    assert res.get_physical_used('vdo1') == 0
    assert res.physical_used == 0

    assert res.logical_size == 1046277
    assert res.get_logical_blocks('vdo1') == 1046277

    assert res.logical_used == 0
    assert res.get_logical_used('vdo1') == 0

    assert res.get_logical_free('vdo1') == 1046277
    assert res.get_physical_free('vdo1') == 1047868

    assert res.get_savings_ratio('vdo1') == 0
    assert res.get_savings_ratio('vdo2') == 14.0

    assert res.get_logical_free_savings_ratio_pct('vdo2') == 37333.29


def test_documentation():
    """
    Here we test the examples in the documentation automatically using
    doctest.  We set up an environment which is similar to what a rule
    writer might see - a 'vdo status' output and key size calculation
    that has been passed in as a parameter to the rule declaration.
    """
    env = {'vdo': VDOStatusCalculation(VDOStatus(context_wrap(INPUT_FULL)))}
    failed, total = doctest.testmod(vdo_status_calculation, globs=env)
    assert failed == 0


def test_exp():
    """
    Here test the examples cause expections
    """
    with pytest.raises(ParseException) as sc1:
        VDOStatusCalculation(context_wrap(''))
    assert "couldn't parse yaml" in str(sc1)
