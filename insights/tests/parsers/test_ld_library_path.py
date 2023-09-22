import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import ld_library_path
from insights.parsers.ld_library_path import UserLdLibraryPath
from insights.tests import context_wrap

LD_LIBRARY_PATH_EMPTY = """
""".strip()

LD_LIBRARY_PATH_INVALID = """
LD_LIBRARY_PATH: Undefined variable.
""".strip()

LD_LIBRARY_PATH_DOC = """
sr1adm /usr/sap/RH1/SYS/exe/run:/usr/sap/RH1/SYS/exe/uc/linuxx86_64:/sapdb/clients/RH1/lib
sr2adm
rh1adm /usr/sap/RH1/SYS/exe/uc/linuxx86_64:/usr/sap/RH1/SYS/exe/run
""".strip()

LD_LIBRARY_PATH = """
sr1adm /usr/sap/RH1/SYS/exe/run:/usr/sap/RH1/SYS/exe/uc/linuxx86_64:/sapdb/clients/RH1/lib
sr2adm "/usr/sap/RH1/SYS/exe/uc/linuxx86_64:/usr/sap/RH1/SYS/exe/run"
sr3adm
rh1adm ''
""".strip()  # noqa: W391


def test_ld_library_path():
    ret = UserLdLibraryPath(context_wrap(LD_LIBRARY_PATH))
    assert len(ret) == 4
    assert ret[0].raw == LD_LIBRARY_PATH.splitlines()[0].split()[-1]
    assert ret[1].raw == LD_LIBRARY_PATH.splitlines()[1].split()[-1]
    assert ret[2].user == 'sr3adm'
    assert ret[2].raw == ''
    assert ret[2].path == ['']
    assert ret[3].user == 'rh1adm'
    assert ret[3].raw == "''"
    assert ret[3].path == ['']
    for p in LD_LIBRARY_PATH.splitlines()[0].split()[-1].split(':'):
        assert p in ret[0].path
    for p in LD_LIBRARY_PATH.splitlines()[1].split()[-1].strip('"').split(':'):
        assert p in ret[1].path


def test_empty_and_invalid():
    with pytest.raises(SkipComponent):
        UserLdLibraryPath(context_wrap(LD_LIBRARY_PATH_EMPTY))


def test_doc_examples():
    env = {
        'ld_lib_path': UserLdLibraryPath(context_wrap(LD_LIBRARY_PATH_DOC)),
    }
    failed, total = doctest.testmod(ld_library_path, globs=env)
    assert failed == 0
