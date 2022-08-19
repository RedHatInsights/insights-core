from insights.parsers.journalctl_header import JournalctlHeader
from insights.parsers import journalctl_header
from insights.tests import context_wrap
import doctest


JOURNAL_FIRLDS_NUMBER = """
8
""".strip()


def test_sys_fs_cgroup_memory_tasks_number():
    journalctl_header = JournalctlHeader(context_wrap(JOURNAL_FIRLDS_NUMBER))
    assert journalctl_header.number == 8


def test_losetup_doc_examples():
    env = {'journalctl_header': JournalctlHeader(context_wrap(JOURNAL_FIRLDS_NUMBER))}
    failed, total = doctest.testmod(journalctl_header, globs=env)
    assert failed == 0
