
import pytest
import doctest

from insights.core.exceptions import SkipComponent
from insights.parsers import ossl_files
from insights.tests import context_wrap

OSSL_FILES_CONFIG_CONTENT = """
/etc/pki/tls/openssl.cnf
""".strip()

OSSL_FILES_CONFIG_ERROR_1 = """
bash: /usr/lib/dracut/ossl-files: No such file or directory
""".strip()

OSSL_FILES_CONFIG_ERROR_2 = """
Error on line 11 of configuration file
00DE01245E7F0000:error:07000065:configuration file routines:def_load_bio:missing equal s    sign:crypto/conf/conf_def.c:525:HERE-->legacyline 11
""".strip()

OSSL_FILES_CONFIG_ERROR_3 = """

""".strip()

OSSL_FILES_CONFIG_CONTENT2 = """
         /etc/pki/tls/openssl.cnf
""".strip()


def test_ossl_files():
    ethtool_priv_flags = ossl_files.OsslFilesConfig(context_wrap(OSSL_FILES_CONFIG_CONTENT))
    assert ethtool_priv_flags.conf_path == "/etc/pki/tls/openssl.cnf"


def test_ossl_files_2():
    ethtool_priv_flags = ossl_files.OsslFilesConfig(context_wrap(OSSL_FILES_CONFIG_CONTENT2))
    assert ethtool_priv_flags.conf_path == "/etc/pki/tls/openssl.cnf"


def test_ossl_files_error1():
    ethtool_priv_flags = ossl_files.OsslFilesConfig(context_wrap(OSSL_FILES_CONFIG_ERROR_1))
    assert ethtool_priv_flags.error_lines == ["bash: /usr/lib/dracut/ossl-files: No such file or directory"]


def test_ossl_files_error2():
    ethtool_priv_flags = ossl_files.OsslFilesConfig(context_wrap(OSSL_FILES_CONFIG_ERROR_2))
    assert ethtool_priv_flags.error_lines[0] == "Error on line 11 of configuration file"


def test_ossl_files_exception():
    with pytest.raises(SkipComponent):
        ossl_files.OsslFilesConfig(context_wrap(OSSL_FILES_CONFIG_ERROR_3))


def test_ethtool_i_doc_examples():
    env = {
        'openssl_cnf': ossl_files.OsslFilesConfig(context_wrap(OSSL_FILES_CONFIG_CONTENT)),
    }
    failed, total = doctest.testmod(ossl_files, globs=env)
    assert failed == 0
