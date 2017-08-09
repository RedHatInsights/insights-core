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
