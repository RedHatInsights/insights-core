import doctest

import pytest
from insights.parsers import slabinfo, SkipException
from insights.parsers.slabinfo import SlabInfo
from insights.tests import context_wrap


PROC_SLABINFO = """
slabinfo - version: 2.1
# name            <active_objs> <num_objs> <objsize> <objperslab> <pagesperslab> : tunables <limit> <batchcount> <sharedfactor> : slabdata <active_slabs> <num_slabs> <sharedavail>
sw_flow                0      0   1256   13    4 : tunables    0    0    0 : slabdata      0      0      0
nf_conntrack_ffffffffaf313a40     12     12    320   12    1 : tunables    10   20    30 : slabdata      40      50      60
xfs_dqtrx              0      0    528   15    2 : tunables    0    0    0 : slabdata      0      0      0
xfs_dquot              0      0    488    8    1 : tunables    0    0    0 : slabdata      0      0      0
xfs_ili             2264   2736    168   24    1 : tunables    0    0    0 : slabdata    114    114      0
xfs_inode           4857   5120    960    8    2 : tunables    0    0    0 : slabdata    640    640      0
xfs_efd_item          76     76    416   19    2 : tunables    0    0    0 : slabdata      4      4      0
xfs_btree_cur         18     18    216   18    1 : tunables    0    0    0 : slabdata      1      1      0
xfs_log_ticket        22     22    184   22    1 : tunables    0    0    0 : slabdata      1      1      0
bio-3                 60     60    320   12    1 : tunables    0    0    0 : slabdata      5      5      0
kcopyd_job             0      0   3312    9    8 : tunables    0    0    0 : slabdata      0      0      0
dm_uevent              0      0   2608   12    8 : tunables    0    0    0 : slabdata      0      0      0
dm_rq_target_io        0      0    136   30    1 : tunables    0    0    0 : slabdata      0      0      0
ip6_dst_cache         72     72    448    9    1 : tunables    0    0    0 : slabdata      8      8      0
RAWv6                 13     13   1216   13    4 : tunables    0    0    0 : slabdata      1      1      0
UDPLITEv6              0      0   1216   13    4 : tunables    0    0    0 : slabdata      0      0      0
UDPv6                 13     13   1216   13    4 : tunables    0    0    0 : slabdata      1      1      0
tw_sock_TCPv6          0      0    256   16    1 : tunables    0    0    0 : slabdata      0      0      0
TCPv6                 15     15   2112   15    8 : tunables    0    0    0 : slabdata      1      1      0
cfq_queue              0      0    232   17    1 : tunables    0    0    0 : slabdata      0      0      0
bsg_cmd                0      0    312   13    1 : tunables    0    0    0 : slabdata      0      0      0
mqueue_inode_cache      9      9    896    9    2 : tunables    0    0    0 : slabdata      1      1      0
hugetlbfs_inode_cache     13     13    608   13    2 : tunables    0    0    0 : slabdata      1      1      0
configfs_dir_cache      0      0     88   46    1 : tunables    0    0    0 : slabdata      0      0      0
dquot                  0      0    256   16    1 : tunables    0    0    0 : slabdata      0      0      0
kioctx                 0      0    576   14    2 : tunables    0    0    0 : slabdata      0      0      0
userfaultfd_ctx_cache      0      0    192   21    1 : tunables    0    0    0 : slabdata      0      0      0
dio                   12     12    640   12    2 : tunables    0    0    0 : slabdata      1      1      0
pid_namespace          0      0   2200   14    8 : tunables    0    0    0 : slabdata      0      0      0
posix_timers_cache     64     64    248   16    1 : tunables    0    0    0 : slabdata      4      4      0
UDP-Lite               0      0   1088   15    4 : tunables    0    0    0 : slabdata      0      0      0
flow_cache             0      0    144   28    1 : tunables    0    0    0 : slabdata      0      0      0
UDP                   15     15   1088   15    4 : tunables    0    0    0 : slabdata      1      1      0
tw_sock_TCP            0      0    256   16    1 : tunables    0    0    0 : slabdata      0      0      0
TCP                    8      8   1984    8    4 : tunables    0    0    0 : slabdata      1      1      0
dax_cache             10     10    768   10    2 : tunables    0    0    0 : slabdata      1      1      0
blkdev_integrity       0      0    112   36    1 : tunables    0    0    0 : slabdata      0      0      0
blkdev_queue          13     13   2456   13    8 : tunables    0    0    0 : slabdata      1      1      0
blkdev_ioc            78     78    104   39    1 : tunables    0    0    0 : slabdata      2      2      0
user_namespace         8      8    480    8    1 : tunables    0    0    0 : slabdata      1      1      0
dmaengine-unmap-128     15     15   1088   15    4 : tunables    0    0    0 : slabdata      1      1      0
sock_inode_cache     216    216    640   12    2 : tunables    0    0    0 : slabdata     18     18      0
fsnotify_mark_connector 136680 136680     24  170    1 : tunables    0    0    0 : slabdata    804    804      0
net_namespace          6      6   5248    6    8 : tunables    0    0    0 : slabdata      1      1      0
shmem_inode_cache    840    840    680   12    2 : tunables    0    0    0 : slabdata     70     70      0
Acpi-State           153    153     80   51    1 : tunables    0    0    0 : slabdata      3      3      0
task_delay_info      180    180    112   36    1 : tunables    0    0    0 : slabdata      5      5      0
taskstats             12     12    328   12    1 : tunables    0    0    0 : slabdata      1      1      0
proc_inode_cache    1199   1308    656   12    2 : tunables    0    0    0 : slabdata    109    109      0
sigqueue              25     25    160   25    1 : tunables    0    0    0 : slabdata      1      1      0
bdev_cache            19     19    832   19    4 : tunables    0    0    0 : slabdata      1      1      0
kernfs_node_cache  15028  15028    120   34    1 : tunables    0    0    0 : slabdata    442    442      0
mnt_cache            907    990    384   10    1 : tunables    0    0    0 : slabdata     99     99      0
inode_cache        14183  14183    592   13    2 : tunables    0    0    0 : slabdata   1091   1091      0
dentry             25349  25662    192   21    1 : tunables    0    0    0 : slabdata   1222   1222      0
iint_cache             0      0    128   32    1 : tunables    0    0    0 : slabdata      0      0      0
avc_xperms_node      292    292     56   73    1 : tunables    0    0    0 : slabdata      4      4      0
avc_node            2408   2408     72   56    1 : tunables    0    0    0 : slabdata     43     43      0
selinux_inode_security  22032  22032     40  102    1 : tunables    0    0    0 : slabdata    216    216      0
buffer_head         4017   4407    104   39    1 : tunables    0    0    0 : slabdata    113    113      0
vm_area_struct      3880   4194    216   18    1 : tunables    0    0    0 : slabdata    233    233      0
mm_struct             50     50   1600   10    4 : tunables    0    0    0 : slabdata      5      5      0
fs_cache              64     64     64   64    1 : tunables    0    0    0 : slabdata      1      1      0
files_cache           48     48    640   12    2 : tunables    0    0    0 : slabdata      4      4      0
signal_cache         127    154   1152   14    4 : tunables    0    0    0 : slabdata     11     11      0
sighand_cache        107    135   2112   15    8 : tunables    0    0    0 : slabdata      9      9      0
task_xstate          171    171    832   19    4 : tunables    0    0    0 : slabdata      9      9      0
task_struct          122    147   4208    7    8 : tunables    0    0    0 : slabdata     21     21      0
cred_jar             609    609    192   21    1 : tunables    0    0    0 : slabdata     29     29      0
anon_vma            1836   1836     80   51    1 : tunables    0    0    0 : slabdata     36     36      0
pid                  192    192    128   32    1 : tunables    0    0    0 : slabdata      6      6      0
shared_policy_node   2635   2635     48   85    1 : tunables    0    0    0 : slabdata     31     31      0
numa_policy           15     15    264   15    1 : tunables    0    0    0 : slabdata      1      1      0
radix_tree_node     2878   3052    584   14    2 : tunables    0    0    0 : slabdata    218    218      0
idr_layer_cache      180    180   2112   15    8 : tunables    0    0    0 : slabdata     12     12      0
dma-kmalloc-8192       0      0   8192    4    8 : tunables    0    0    0 : slabdata      0      0      0
dma-kmalloc-4096       0      0   4096    8    8 : tunables    0    0    0 : slabdata      0      0      0
dma-kmalloc-2048       0      0   2048    8    4 : tunables    0    0    0 : slabdata      0      0      0
dma-kmalloc-1024       0      0   1024    8    2 : tunables    0    0    0 : slabdata      0      0      0
dma-kmalloc-512        8      8    512    8    1 : tunables    0    0    0 : slabdata      1      1      0
dma-kmalloc-256        0      0    256   16    1 : tunables    0    0    0 : slabdata      0      0      0
dma-kmalloc-128        0      0    128   32    1 : tunables    0    0    0 : slabdata      0      0      0
dma-kmalloc-64         0      0     64   64    1 : tunables    0    0    0 : slabdata      0      0      0
dma-kmalloc-32         0      0     32  128    1 : tunables    0    0    0 : slabdata      0      0      0
dma-kmalloc-16         0      0     16  256    1 : tunables    0    0    0 : slabdata      0      0      0
dma-kmalloc-8          0      0      8  512    1 : tunables    0    0    0 : slabdata      0      0      0
dma-kmalloc-192        0      0    192   21    1 : tunables    0    0    0 : slabdata      0      0      0
dma-kmalloc-96         0      0     96   42    1 : tunables    0    0    0 : slabdata      0      0      0
kmalloc-8192          40     40   8192    4    8 : tunables    0    0    0 : slabdata     10     10      0
kmalloc-4096         255    272   4096    8    8 : tunables    0    0    0 : slabdata     34     34      0
kmalloc-2048         280    296   2048    8    4 : tunables    0    0    0 : slabdata     37     37      0
kmalloc-1024        1135   1152   1024    8    2 : tunables    0    0    0 : slabdata    144    144      0
kmalloc-512          649    760    512    8    1 : tunables    0    0    0 : slabdata     95     95      0
kmalloc-256         2735   2992    256   16    1 : tunables    0    0    0 : slabdata    187    187      0
kmalloc-192         1407   1407    192   21    1 : tunables    0    0    0 : slabdata     67     67      0
kmalloc-128         1664   1664    128   32    1 : tunables    0    0    0 : slabdata     52     52      0
kmalloc-96          1470   1470     96   42    1 : tunables    0    0    0 : slabdata     35     35      0
kmalloc-64         40126  40640     64   64    1 : tunables    0    0    0 : slabdata    635    635      0
kmalloc-32        134702 135552     32  128    1 : tunables    0    0    0 : slabdata   1059   1059      0
kmalloc-16         65792  65792     16  256    1 : tunables    0    0    0 : slabdata    257    257      0
kmalloc-8          87552  87552      8  512    1 : tunables    0    0    0 : slabdata    171    171      0
kmem_cache_node      128    128     64   64    1 : tunables    0    0    0 : slabdata      2      2      0
kmem_cache           112    111    256   16    1 : tunables    10   20   30 : slabdata    17     18     19
""".strip()

SLABINFO_DOC = """
slabinfo - version: 2.1
# name            <active_objs> <num_objs> <objsize> <objperslab> <pagesperslab> : tunables <limit> <batchcount> <sharedfactor> : slabdata <active_slabs> <num_slabs> <sharedavail>
sw_flow                0      0   1256   13    4 : tunables    0    0    0 : slabdata      0      0      0
nf_conntrack_ffffffffaf313a40     12     12    320   12    1 : tunables    0    0    0 : slabdata      1      1      0
xfs_dqtrx              0      0    528   15    2 : tunables    0    0    0 : slabdata      0      0      0
xfs_dquot              0      0    488    8    1 : tunables    0    0    0 : slabdata      0      0      0
xfs_ili             2264   2736    168   24    1 : tunables    0    0    0 : slabdata    114    114      0
xfs_inode           4845   5120    960    8    2 : tunables    0    0    0 : slabdata    640    640      0
xfs_efd_item          76     76    416   19    2 : tunables    0    0    0 : slabdata      4      4      0
xfs_btree_cur         18     18    216   18    1 : tunables    0    0    0 : slabdata      1      1      0
xfs_log_ticket        22     22    184   22    1 : tunables    0    0    0 : slabdata      1      1      0
bio-3                 60     60    320   12    1 : tunables    0    0    0 : slabdata      5      5      0
kcopyd_job             0      0   3312    9    8 : tunables    0    0    0 : slabdata      0      0      0
dm_uevent              0      0   2608   12    8 : tunables    0    0    0 : slabdata      0      0      0
dm_rq_target_io        0      0    136   30    1 : tunables    0    0    0 : slabdata      0      0      0
ip6_dst_cache         72     72    448    9    1 : tunables    0    0    0 : slabdata      8      8      0
RAWv6                 13     13   1216   13    4 : tunables    0    0    0 : slabdata      1      1      0
UDPLITEv6              0      0   1216   13    4 : tunables    0    0    0 : slabdata      0      0      0
UDPv6                 13     13   1216   13    4 : tunables    0    0    0 : slabdata      1      1      0
tw_sock_TCPv6          0      0    256   16    1 : tunables    0    0    0 : slabdata      0      0      0
TCPv6                 15     15   2112   15    8 : tunables    0    0    0 : slabdata      1      1      0
cfq_queue              0      0    232   17    1 : tunables    0    0    0 : slabdata      0      0      0
bsg_cmd                0      0    312   13    1 : tunables    10   20   30 : slabdata     40     50     60
""".strip()

SLABINFO_DETAILS = """
""".strip()

SLABINFO_DETAILS_2 = """
# name            <active_objs> <num_objs> <objsize> <objperslab> <pagesperslab> : tunables <limit> <batchcount> <sharedfactor> : slabdata <active_slabs> <num_slabs> <sharedavail>
cfq_queue              0      0    232   17    1 : tunables    0    0    0 : slabdata      0      0      0
bsg_cmd                0      0    312   13    1 : tunables    10   20   30 : slabdata     40     50     60
""".strip()

SLABINFO_DETAILS_3 = """
slabinfo - version: 2.1
cfq_queue              0      0    232   17    1 : tunables    0    0    0 : slabdata      0      0      0
bsg_cmd                0      0    312   13    1 : tunables    10   20   30 : slabdata     40     50     60
""".strip()

SLABINFO_DETAILS_LEN_MISS_MATCH = """
slabinfo - version: 2.1
# name            <active_objs> <num_objs> <objsize> <objperslab> <pagesperslab> : tunables <limit> <batchcount> <sharedfactor> : slabdata <active_slabs> <num_slabs> <sharedavail>
sw_flow                0      0   1256   13    4 : tunables    0    0    0 : slabdata      0      0      0      100     1220
nf_conntrack_ffffffffaf313a40     12     12    320   12    1 : tunables    0    0    0 : slabdata      1      1      10     100
""".strip()


def test_check_slabinfo():
    result = SlabInfo(context_wrap(PROC_SLABINFO))
    assert len(result.data.keys()) == 103
    assert result.slab_object('kcopyd_job', 'objsize') == 3312
    assert result.slab_object('kmalloc-16', 'objsize') == 16
    assert result.slab_object('kmalloc-16', 'name') is None
    assert result.slab_version == '2.1'
    result.slab_details('kmem_cache') == {'name': 'kmem_cache', 'active_objs': '112', 'num_objs': '111', 'objsize': '256', 'objperslab': '16', 'pagesperslab': '1', 'limit': '10', 'batchcount': '20', 'sharedfactor': '30', 'active_slabs': '17', 'num_slabs': '18', 'sharedavail': '19'}


def test_slabinfo_doc_examples():
    env = {
        'pslabinfo': SlabInfo(context_wrap(SLABINFO_DOC))
    }
    failed, total = doctest.testmod(slabinfo, globs=env)
    assert failed == 0


def test_slabinfo_exception():
    with pytest.raises(SkipException) as exc:
        pslabinfo = SlabInfo(context_wrap(SLABINFO_DETAILS))
        assert pslabinfo is None
    assert 'No Contents' in str(exc)

    with pytest.raises(SkipException) as exc:
        pslabinfo_1 = SlabInfo(context_wrap(SLABINFO_DETAILS_2))
        assert pslabinfo_1 is None
    assert 'Invalid Contents' in str(exc)

    with pytest.raises(SkipException) as exc:
        pslabinfo_2 = SlabInfo(context_wrap(SLABINFO_DETAILS_3))
        assert pslabinfo_2 is None
    assert 'Invalid Contents' in str(exc)

    with pytest.raises(SkipException) as exc_1:
        pslabinfo_3 = SlabInfo(context_wrap(SLABINFO_DETAILS_LEN_MISS_MATCH))
        assert pslabinfo_3 is None
    assert 'Invalid Contents' in str(exc_1)
