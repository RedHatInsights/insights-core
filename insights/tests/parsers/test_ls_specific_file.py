import doctest
import pytest
from insights.core.exceptions import SkipComponent
from insights.parsers import ls_specific_file
from insights.parsers.ls_specific_file import LSladSpecificFile
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
    list_specific_file = ls_specific_file.LSladSpecificFile(context_wrap(LS_FSTAB))
    assert len(list_specific_file) == 2
    assert '/boot' in list_specific_file
    assert list_specific_file.get('/') == {'type': 'd', 'perms': 'r-xr-xr-x.', 'links': 21, 'owner': 'root', 'group': 'root', 'size': 4096, 'date': 'Oct 15 08:19', 'name': '/', 'raw_entry': 'dr-xr-xr-x. 21 root root 4096 Oct 15 08:19 /', 'dir': ''}


def test_ls_fstab_error():
    with pytest.raises(SkipComponent):
        LSladSpecificFile(context_wrap(LS_FSTAB_EMPTY))


def test_doc_examples():
    env = {"ls_specific_file": LSladSpecificFile(context_wrap(LS_FSTAB))}
    failed, total = doctest.testmod(ls_specific_file, globs=env)
    assert failed == 0
