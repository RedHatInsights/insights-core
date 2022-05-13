from insights.parsers import mdadm
from insights.parsers.mdadm import MDAdmMetadata
from insights.tests import context_wrap

import doctest

MDADM_CONTENT = """
/dev/loop0:
Magic : a92b4efc
Version : 1.0
Feature Map : 0x0
Array UUID : 98e098ef:c8662ce2:2ed2aa5f:7f0416a9
Name : 0
Creation Time : Mon Jun 29 02:16:52 2020
Raid Level : raid1
Raid Devices : 2

Avail Dev Size : 16383968 sectors (7.81 GiB 8.39 GB)
Array Size : 1048576 KiB (1024.00 MiB 1073.74 MB)
Used Dev Size : 2097152 sectors (1024.00 MiB 1073.74 MB)
Super Offset : 16383984 sectors
Unused Space : before=0 sectors, after=14286824 sectors
State : clean
Device UUID : 5e249ed9:a9ee800a:c09c963f:363a18d2

Update Time : Mon Jun 29 02:19:56 2020
Bad Block Log : 512 entries available at offset -8 sectors
Checksum : 395066e8 - correct
Events : 60

Device Role : Active device 0
Array State : AA ('A' == active, '.' == missing, 'R' == replacing)
"""  # noqa


def test_doc_examples():
    env = {
        'mdadm': MDAdmMetadata(context_wrap(
            MDADM_CONTENT, path='insights_commands/mdadm_-E_.dev.loop0'
        )),
    }
    failed, total = doctest.testmod(mdadm, globs=env)
    assert failed == 0


def test_mdadm():
    md = MDAdmMetadata(context_wrap(
        MDADM_CONTENT, path='insights_commands/mdadm_-E_.dev.loop0'
    ))

    # Device assertions
    assert md.device == '/dev/loop0'

    # Information assertions
    assert md['Update Time'] == 'Mon Jun 29 02:19:56 2020'
    assert md['Array Size'] == '1048576 KiB (1024.00 MiB 1073.74 MB)'
