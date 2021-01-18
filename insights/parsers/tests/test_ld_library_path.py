from insights.parsers.ld_library_path import LdLibraryPath
from insights.tests import context_wrap
from insights.parsers import ld_library_path, SkipException
import doctest
import pytest

LD_LIBRARY_PATH_EMPTY = """
""".strip()

LD_LIBRARY_PATH_EMPTY_1 = """
LD_LIBRARY_PATH: Undefined variable.
""".strip()

LD_LIBRARY_PATH_DOC = """
/usr/sap/RH1/SYS/exe/run:/usr/sap/RH1/SYS/exe/uc/linuxx86_64:/sapdb/clients/RH1/lib
""".strip()

LD_LIBRARY_PATH = """
tset: standard error: Inappropriate ioctl for device

/usr/sap/SR1/HDB02/exe/krb5/lib/krb5/plugins/preauth:/usr/sap/SR1/HDB02/exe/krb5/lib:/usr/sap/SR1/HDB02/exe:/usr/sap/SR1/HDB02/exe/Python/lib:/usr/sap/SR1/HDB02/exe/filter:/usr/sap/SR1/HDB02/exe/dat_bin_dir:/usr/sap/SR1/HDB02/exe/plugins/afl
""".strip()


def test_proc_environ():
    ret = LdLibraryPath(context_wrap(LD_LIBRARY_PATH, path='insights_commands/su_-l_sr1adm_-c_echo_LD_LIBRARY_PATH'))
    assert len(ret) == 7
    for p in LD_LIBRARY_PATH.splitlines()[-1].split(':'):
        assert p in ret
    ret.user = 'sr1adm'


def test_empty_and_invalid():
    with pytest.raises(SkipException):
        LdLibraryPath(context_wrap(LD_LIBRARY_PATH_EMPTY))

    with pytest.raises(SkipException):
        LdLibraryPath(context_wrap(LD_LIBRARY_PATH_EMPTY_1))


def test_doc_examples():
    env = {
        'ld_lib_path': LdLibraryPath(context_wrap(LD_LIBRARY_PATH_DOC, path='insights_commands/su_-l_sr2adm_-c_echo_LD_LIBRARY_PATH')),
    }
    failed, total = doctest.testmod(ld_library_path, globs=env)
    assert failed == 0
