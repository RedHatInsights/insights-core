import doctest
import pytest
from insights.core.exceptions import SkipComponent
from insights.parsers import ls_fstab
from insights.parsers.ls_fstab import LsFSTab
from insights.tests import context_wrap

LS_FSTAB = """
ls: cannot access 'swap': No such file or directory
dr-xr-xr-x. 21 root root 4096 Oct 15 08:19 /
drwxr-xr-x.  2 root root    6 Nov  9  2021 /boot
""".strip()

LS_FSTAB_EMPTY = """
ls: cannot access 'swap': No such file or directory
ls: cannot access '/boot': No such file or directory
ls: cannot access 'none': No such file or directory
""".strip()


def test_ls_fstab():
    list_fstab = ls_fstab.LsFSTab(context_wrap(LS_FSTAB))
    assert len(list_fstab.entries) == 2
    assert '/boot' in list_fstab.entries
    assert list_fstab.entries.get('/') == {'type': 'd', 'perms': 'r-xr-xr-x.', 'links': 21, 'owner': 'root', 'group': 'root', 'size': 4096, 'date': 'Oct 15 08:19', 'name': '/', 'raw_entry': 'dr-xr-xr-x. 21 root root 4096 Oct 15 08:19 /', 'dir': ''}


def test_ls_fstab_error():
    with pytest.raises(SkipComponent):
        LsFSTab(context_wrap(LS_FSTAB_EMPTY))


def test_doc_examples():
    env = {"ls_fstab": LsFSTab(context_wrap(LS_FSTAB))}
    failed, total = doctest.testmod(ls_fstab, globs=env)
    assert failed == 0
