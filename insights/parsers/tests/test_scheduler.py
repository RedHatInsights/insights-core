import doctest

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


def test_schedulers_defaults():
    r = scheduler.Scheduler(context_wrap('[none] mq-deadline kyber bfq',
                                         '/sys/block/nvme0n1/queue/scheduler'))
    assert r.device == 'nvme0n1'
    assert r.schedulers == ['none', 'mq-deadline', 'kyber', 'bfq']
    assert r.active_scheduler == 'none'

    # RHEL 6
    r = scheduler.Scheduler(context_wrap('noop anticipatory deadline [cfq]',
                                         '/sys/block/vda/queue/scheduler'))
    assert r.device == 'vda'
    assert r.schedulers == ['noop', 'anticipatory', 'deadline', 'cfq']
    assert r.active_scheduler == 'cfq'

    # RHEL 7
    r = scheduler.Scheduler(context_wrap('[mq-deadline] kyber none',
                                         '/sys/block/vda/queue/scheduler'))
    assert r.device == 'vda'
    assert r.schedulers == ['mq-deadline', 'kyber', 'none']
    assert r.active_scheduler == 'mq-deadline'

    # RHEL 8
    r = scheduler.Scheduler(context_wrap('[mq-deadline] kyber bfq none',
                                         '/sys/block/vda/queue/scheduler'))
    assert r.device == 'vda'
    assert r.schedulers == ['mq-deadline', 'kyber', 'bfq', 'none']
    assert r.active_scheduler == 'mq-deadline'


def test_none():
    r = scheduler.Scheduler(context_wrap('none',
                                         '/sys/block/vda/queue/scheduler'))
    assert r.device == 'vda'
    assert r.schedulers == ['none']
    assert r.active_scheduler is None
    assert r.data == {}


def test_docs():
    env = {
        'scheduler_obj': scheduler.Scheduler(context_wrap(SDA_SCHEDULER, SDA_PATH))
    }
    failed, total = doctest.testmod(scheduler, globs=env)
    assert failed == 0
