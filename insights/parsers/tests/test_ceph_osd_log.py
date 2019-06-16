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

from insights.parsers.ceph_osd_log import CephOsdLog
from insights.tests import context_wrap

from datetime import datetime

CEPH_OSD_LOG = """
2015-10-30 09:09:30.334033 7f12c6f8b700  0 -- 10.1.26.72:6851/1003139 >> 10.1.26.64:6800/1005943 pipe(0x14f3b000 sd=464 :6851 s=0 pgs=0 cs=0 l=0 c=0xfe3a840).accept connect_seq 30 vs existing 29 state standby
2015-10-30 10:18:38.691642 7f1301f37700  0 -- 10.1.26.72:6851/1003139 >> 10.1.26.56:6820/1004150 pipe(0x6c79000 sd=275 :6851 s=0 pgs=0 cs=0 l=0 c=0x1504cf20).accept connect_seq 2 vs existing 1 state standby
2015-10-30 10:18:58.266050 7f12e97b1700  0 -- 10.1.26.72:6851/1003139 >> 10.1.26.23:6830/30212 pipe(0x10759000 sd=629 :6851 s=2 pgs=22 cs=1 l=0 c=0x10178160).fault, initiating reconnect
""".strip()

matched_lines = ['2015-10-30 09:09:30.334033 7f12c6f8b700  0 -- 10.1.26.72:6851/1003139 >> 10.1.26.64:6800/1005943 pipe(0x14f3b000 sd=464 :6851 s=0 pgs=0 cs=0 l=0 c=0xfe3a840).accept connect_seq 30 vs existing 29 state standby', '2015-10-30 10:18:38.691642 7f1301f37700  0 -- 10.1.26.72:6851/1003139 >> 10.1.26.56:6820/1004150 pipe(0x6c79000 sd=275 :6851 s=0 pgs=0 cs=0 l=0 c=0x1504cf20).accept connect_seq 2 vs existing 1 state standby']


def test_ceph_osd_log():
    ceph_osd_log_obj = CephOsdLog(context_wrap(CEPH_OSD_LOG))
    assert "initiating reconnect" in ceph_osd_log_obj
    assert CEPH_OSD_LOG.splitlines()[1] == ceph_osd_log_obj.get('state standby')[1]['raw_message']
    assert sorted([i['raw_message'] for i in ceph_osd_log_obj.get_after(datetime(2015, 10, 30, 10, 0, 0))]) == [
        '2015-10-30 10:18:38.691642 7f1301f37700  0 -- 10.1.26.72:6851/1003139 >> 10.1.26.56:6820/1004150 pipe(0x6c79000 sd=275 :6851 s=0 pgs=0 cs=0 l=0 c=0x1504cf20).accept connect_seq 2 vs existing 1 state standby',
        '2015-10-30 10:18:58.266050 7f12e97b1700  0 -- 10.1.26.72:6851/1003139 >> 10.1.26.23:6830/30212 pipe(0x10759000 sd=629 :6851 s=2 pgs=22 cs=1 l=0 c=0x10178160).fault, initiating reconnect'
    ]
