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

from insights.parsers import scheduler
from insights.tests import context_wrap

SDA_SCHEDULER = '''
noop deadline [cfq]
'''.strip()

SDB_SCHEDULER = '''
noop [deadline] cfq
'''.strip()

VDC_SCHEDULER = '''
[noop] deadline cfq
'''.strip()

SDA_PATH = "/sys/block/sda/queue/scheduler"
SDB_PATH = "/sys/block/sdb/queue/scheduler"
VDC_PATH = "/sys/block/vdc/queue/scheduler"


def test_scheduler_cfq():
    r = scheduler.Scheduler(context_wrap(SDA_SCHEDULER, SDA_PATH))
    assert r.data["sda"] == '[cfq]'


def test_scheduler_deadline():
    r = scheduler.Scheduler(context_wrap(SDB_SCHEDULER, SDB_PATH))
    assert r.data["sdb"] == '[deadline]'


def test_scheduler_noop():
    r = scheduler.Scheduler(context_wrap(VDC_SCHEDULER, VDC_PATH))
    assert r.data["vdc"] == '[noop]'
