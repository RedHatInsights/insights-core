import doctest
import pytest
from insights.parsers import ulimit
from insights.parsers.ulimit import UlimitHard, UlimitSoft
from insights.tests import context_wrap

ULIMIT_SOFT = """
core file size          (blocks, -c) 0
data seg size           (kbytes, -d) unlimited
scheduling priority             (-e) 0
file size               (blocks, -f) unlimited
pending signals                 (-i) 15003
max locked memory       (kbytes, -l) 16384
max memory size         (kbytes, -m) unlimited
open files                      (-n) 1024
pipe size            (512 bytes, -p) 8
POSIX message queues     (bytes, -q) 819200
stack size              (kbytes, -s) 30720
cpu time               (seconds, -t) unlimited
max user processes              (-u) 15003
virtual memory          (kbytes, -v) unlimited
file locks                      (-x) unlimited
""".strip()

ULIMIT_HARD = """
core file size          (blocks, -c) 100
data seg size           (kbytes, -d) unlimited
scheduling priority             (-e) 0
file size               (blocks, -f) unlimited
pending signals                 (-i) 15003
max locked memory       (kbytes, -l) 16384
max memory size         (kbytes, -m) unlimited
open files                      (-n) 4096
pipe size            (512 bytes, -p) 8
POSIX message queues     (bytes, -q) 819200
real-time priority              (-r) 0
stack size              (kbytes, -s) 30720
cpu time               (seconds, -t) unlimited
max user processes              (-u) 15003
virtual memory          (kbytes, -v) unlimited
file locks                      (-x) unlimited
""".strip()


def test_ulimit_hard():
    uh = UlimitHard(context_wrap(ULIMIT_HARD))
    assert len(uh) == 16
    assert 'cpu_time' in uh
    assert 'real-time_priority' in uh
    assert uh['cpu_time'].limits_value == 'unlimited'
    assert uh['file_locks'].limits_value == 'unlimited'
    assert uh['core_file_size'].limits_value == 100
    assert uh['POSIX_message_queues'].limits_value == 819200


def test_ulimit_soft():
    uh = UlimitSoft(context_wrap(ULIMIT_SOFT))
    assert len(uh) == 15
    assert 'cpu_time' in uh
    assert 'real-time_priority' not in uh
    assert uh['cpu_time'].limits_value == 'unlimited'
    assert uh['file_locks'].limits_value == 'unlimited'
    assert uh['core_file_size'].limits_value == 0
    assert uh['POSIX_message_queues'].limits_value == 819200


def test_ulimit_doc_examples():
    env = {
        'ulimit_hard': UlimitHard(context_wrap(ULIMIT_HARD)),
        'ulimit_soft': UlimitSoft(context_wrap(ULIMIT_SOFT)),
    }
    failed, total = doctest.testmod(ulimit, globs=env)
    assert failed == 0
