import doctest
import pytest
from insights.parsers import SkipException, ulimit
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
    assert uh['cpu_time'].value == 'unlimited'
    assert uh['file_locks'].value == 'unlimited'
    assert uh['core_file_size'].value == 100
    assert uh['POSIX_message_queues'].value == 819200
    assert sorted(uh['pipe_size'].details) == sorted(['512 bytes', '-p'])


def test_ulimit_soft():
    us = UlimitSoft(context_wrap(ULIMIT_SOFT))
    assert len(us) == 15
    assert 'cpu_time' in us
    assert 'real-time_priority' not in us
    assert us['cpu_time'].value == 'unlimited'
    assert us['file_locks'].value == 'unlimited'
    assert us['core_file_size'].value == 0
    assert us['POSIX_message_queues'].value == 819200
    assert sorted(us['pipe_size'].details) == sorted(['512 bytes', '-p'])


def test_ulimit_exp():
    with pytest.raises(SkipException):
        UlimitSoft(context_wrap(""))


def test_ulimit_doc_examples():
    env = {
        'ulimit_hard': UlimitHard(context_wrap(ULIMIT_HARD)),
        'ulimit_soft': UlimitSoft(context_wrap(ULIMIT_SOFT)),
    }
    failed, total = doctest.testmod(ulimit, globs=env)
    assert failed == 0
