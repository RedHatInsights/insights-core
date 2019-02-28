"""
Crash log ``vmcore-dmesg.txt``
==============================

This module provides ``vmcore-dmesg.txt`` crash logs that are stored in ``/var/crash/[host]-YYYY-MM-DD-HH:MM:SS/``.

Exemplary ``vmcore-dmesg.txt`` looks like::

    [  345.691798] device-mapper: raid: Failed to read superblock of device at position 0
    [  345.693497] device-mapper: raid: Discovered old metadata format; upgrading to extended metadata format
    [  345.701166] md/raid1:mdX: active with 1 out of 2 mirrors
    [  345.726870] BUG: unable to handle kernel NULL pointer dereference at 00000000000005ec
    [  345.727782] IP: [<ffffffffc0852ffb>] read_balance+0x1db/0x4e0 [raid1]
    [  345.728570] PGD 0
    [  345.729279] Oops: 0000 [#1] SMP
    [  345.729950] Modules linked in: raid1 dm_raid raid456 async_raid6_recov async_memcpy async_pq raid6_pq async_xor xor async_tx
    [  345.734752]  drm_kms_helper syscopyarea sysfillrect sysimgblt fb_sys_fops ttm drm bfa ahci crct10dif_pclmul crct10dif_common
    [  345.737334] CPU: 6 PID: 952 Comm: systemd-udevd Kdump: loaded Not tainted 3.10.0-862.9.1.el7.x86_64 #1
    [  345.738198] Hardware name: Dell Inc. PowerEdge R730xd/072T6D, BIOS 2.4.3 01/17/2017
    [  345.739334] task: ffff9f888d030fd0 ti: ffff9f86b76b4000 task.ti: ffff9f86b76b4000

The class inherites LogFileOutput and doesn't implement new methods/attributes.
vmcore_dmesg defined in Specs allowes multioutput parsing. Filtering is allowed.

Examples:
    >>> vmcore_dmesg.get("Modules linked in:")
    [{'raw_message': '[  345.729950] Modules linked in: raid1 dm_raid raid456 async_raid6_recov async_memcpy async_pq raid6_pq async_xor xor async_tx'}]
    >>> vmcore_dmesg.get("device-mapper")
    [{'raw_message': '[  345.691798] device-mapper: raid: Failed to read superblock of device at position 0'}, {'raw_message': '[  345.693497] device-mapper: raid: Discovered old metadata format; upgrading to extended metadata format'}]
"""

from .. import parser, LogFileOutput
from insights.specs import Specs


@parser(Specs.vmcore_dmesg)
class VMCoreDmesg(LogFileOutput):
    """
    This class parses data in ``/var/crash/[host]-YYYY-MM-DD-HH:MM:SS/vmcore-dmesg.txt``.
    Inherited from LogFileOutput. See LogFileOutput for details. No new methods or attributes.
    MultiOutput is allowed. Filtering is allowed.
    """
    pass
