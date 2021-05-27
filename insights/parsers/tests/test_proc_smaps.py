import doctest
import pytest
from insights.tests import context_wrap
from insights.parsers import SkipException
from insights.parsers import proc_smaps
from insights.parsers.proc_smaps import ProcSmaps

SWAP_MEM_INFO = """
[{"Size": 5797980, "KernelPageSize": 7016, "MMUPageSize": 7016, "Rss": 164008, "Pss": 149508, "Shared_Clean": 19564, "Shared_Dirty": 100, "Private_Clean": 2176, "Private_Dirty": 142168, "Referenced": 154760, "Anonymous": 142168, "LazyFree": 0, "AnonHugePages": 92160, "ShmemPmdMapped": 0, "Shared_Hugetlb": 0, "Private_Hugetlb": 0, "Swap": 54772, "SwapPss": 54492, "Locked": 0, "PID": 3443, "COMMAND": "/usr/bin/gnome-shell"}, {"Size": 1424700, "KernelPageSize": 1840, "MMUPageSize": 1840, "Rss": 3104, "Pss": 238, "Shared_Clean": 2888, "Shared_Dirty": 0, "Private_Clean": 76, "Private_Dirty": 140, "Referenced": 3104, "Anonymous": 164, "LazyFree": 0, "AnonHugePages": 0, "ShmemPmdMapped": 0, "Shared_Hugetlb": 0, "Private_Hugetlb": 0, "Swap": 486084, "SwapPss": 486084, "Locked": 0, "PID": 3072, "COMMAND": "pmie"}]
""".strip()

SWAP_MEM_EMPTY_DATA = """
""".strip()


def test_proc_smaps():
    swap_mem_info = ProcSmaps(context_wrap(SWAP_MEM_INFO))
    assert swap_mem_info.data[0]['PID'] == 3443
    assert str(swap_mem_info.data[0]['COMMAND']) == '/usr/bin/gnome-shell'
    assert swap_mem_info.data[0]['Swap'] == 54772
    assert swap_mem_info.data[0]['SwapPss'] == 54492


def test_empty():
    with pytest.raises(SkipException) as e:
        ProcSmaps(context_wrap(SWAP_MEM_EMPTY_DATA))
    assert 'No files found.' in str(e)


def test_proc_smaps_doc_example():
    env = {
        'proc_smaps': ProcSmaps(context_wrap(SWAP_MEM_INFO))
    }
    failed, total = doctest.testmod(proc_smaps, globs=env)
    assert failed == 0
