from insights.parsers.ld_library_path import PidLdLibraryPath
from insights.tests import context_wrap
from insights.parsers import ld_library_path, SkipException, ParseException
import doctest
import pytest

LD_LIBRARY_PATH_EMPTY = """
""".strip()

LD_LIBRARY_PATH_INVALID = """
LD_LIBRARY_PATH: Undefined variable.
""".strip()

LD_LIBRARY_PATH_DOC = """
105901 /usr/sap/RH1/SYS/exe/run:/usr/sap/RH1/SYS/exe/uc/linuxx86_64:/sapdb/clients/RH1/lib
105902 /usr/sap/RH1/SYS/exe/uc/linuxx86_64:/usr/sap/RH1/SYS/exe/run
""".strip()

LD_LIBRARY_PATH = """
105901 /usr/sap/RH1/SYS/exe/run:/usr/sap/RH1/SYS/exe/uc/linuxx86_64:/sapdb/clients/RH1/lib
105902 "/usr/sap/RH1/SYS/exe/uc/linuxx86_64:/usr/sap/RH1/SYS/exe/run"
105903 
105904 ''
""".strip()  # noqa: W391


def test_ld_library_path():
    ret = PidLdLibraryPath(context_wrap(LD_LIBRARY_PATH))
    assert len(ret) == 4
    assert ret[0].pid == '105901'
    assert ret[1].pid == '105902'
    assert ret[2].pid == '105903'
    assert ret[1].raw == LD_LIBRARY_PATH.splitlines()[1].split()[-1]
    assert ret[2].raw == ''
    assert ret[3].raw == "''"
    assert ret[2].path == ['']
    assert ret[3].path == ['']
    for p in LD_LIBRARY_PATH.splitlines()[0].split()[-1].split(':'):
        assert p in ret[0].path
    for p in LD_LIBRARY_PATH.splitlines()[1].split()[-1].strip('"').split(':'):
        assert p in ret[1].path


def test_empty_and_invalid():
    with pytest.raises(SkipException):
        PidLdLibraryPath(context_wrap(LD_LIBRARY_PATH_EMPTY))

    with pytest.raises(ParseException):
        PidLdLibraryPath(context_wrap(LD_LIBRARY_PATH_INVALID))


def test_doc_examples():
    env = {
        'ld_lib_path': PidLdLibraryPath(context_wrap(LD_LIBRARY_PATH_DOC)),
    }
    failed, total = doctest.testmod(ld_library_path, globs=env)
    assert failed == 0
