import doctest
import pytest
from insights.tests import context_wrap
from insights.parsers import SkipException
from insights.parsers import proc_swap_memory
from insights.parsers.proc_swap_memory import ProcSwapMemory

SWAP_MEM_INFO = """
[{"pid": 3065, "command": "/usr/libexec/packagekitd", "swap": 348, "swappss": 348}, {"pid": 2873, "command": "/usr/bin/gnome-shell", "swap": 13576, "swappss": 348}, {"pid": 1498, "command": "/usr/bin/mongod -f /etc/mongod.conf", "swap": 2996, "swappss": 2152}, {"pid": 31072, "command": "/opt/google/chrome/chrome", "swap": 4488, "swappss": 4204}]
""".strip()

SWAP_MEM_EMPTY_DATA = """
""".strip()


def test_proc_swap_memory():
    swap_mem_info = ProcSwapMemory(context_wrap(SWAP_MEM_INFO))
    assert len(swap_mem_info.data) == 4
    assert swap_mem_info.data[0]['pid'] == 3065
    assert swap_mem_info.data[0]['command'] == "/usr/libexec/packagekitd"
    assert swap_mem_info.data[0]['swap'] == 348
    assert swap_mem_info.data[0]['swappss'] == 348


def test_empty():
    with pytest.raises(SkipException) as e:
        ProcSwapMemory(context_wrap(SWAP_MEM_EMPTY_DATA))
    assert 'No files found.' in str(e)


def test_proc_swap_memory_doc_example():
    env = {
        'swap_memory_doc_obj': ProcSwapMemory(context_wrap(SWAP_MEM_INFO))
    }
    failed, total = doctest.testmod(proc_swap_memory, globs=env)
    assert failed == 0
