"""
CephOsdLog - file ``var/log/ceph/ceph-osd.*.log``
=================================================

This is a standard log mapper based on the LogFileOutput class.

Sample input::

    2015-10-30 09:09:30.334033 7f12c6f8b700  0 -- 10.1.26.72:6851/1003139 >> 10.1.26.64:6800/1005943 pipe(0x14f3b000 sd=464 :6851 s=0 pgs=0 cs=0 l=0 c=0xfe3a840).accept connect_seq 30 vs existing 29 state standby
    2015-10-30 10:18:58.266050 7f12e97b1700  0 -- 10.1.26.72:6851/1003139 >> 10.1.26.23:6830/30212 pipe(0x10759000 sd=629 :6851 s=2 pgs=22 cs=1 l=0 c=0x10178160).fault, initiating reconnect

Examples:

    >>> logs = shared[CephOsdLog]
    >>> 'initiating reconnect' in logs
    True
    >>> logs.get('pipe')
    ['2015-10-30 09:09:30.334033 7f12c6f8b700  0 -- 10.1.26.72:6851/1003139 >> 10.1.26.64:6800/1005943 pipe(0x14f3b000 sd=464 :6851 s=0 pgs=0 cs=0 l=0 c=0xfe3a840).accept connect_seq 30 vs existing 29 state standby',
     '2015-10-30 10:18:58.266050 7f12e97b1700  0 -- 10.1.26.72:6851/1003139 >> 10.1.26.23:6830/30212 pipe(0x10759000 sd=629 :6851 s=2 pgs=22 cs=1 l=0 c=0x10178160).fault, initiating reconnect']
"""

from .. import LogFileOutput, mapper


@mapper('ceph_osd.log')
class CephOsdLog(LogFileOutput):
    """
    Provide access to Ceph OSD logs using the LogFileOutput mapper class.
    """
    pass
