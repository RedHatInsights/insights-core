import pytest
from insights.parsers import ParseException
from insights.parsers.mysqladmin import MysqladminVars
from insights.tests import context_wrap

INPUT_NORMAL = """
+---------------------------------------------------+-------------------
| Variable_name                                     | Value            |
+---------------------------------------------------+------------------+
| aria_block_size                                   | 8192             |
| aria_checkpoint_interval                          | 30               |
| auto_increment_increment                          | 1                |
| auto_increment_offset                             | 1                |
| binlog_stmt_cache_size                            | 32768            |
| character_set_filesystem                          | binary           |
| datadir                                           | /var/lib/mysql/  |
| init_file                                         |                  |
| innodb_autoinc_lock_mode                          | 1                |
| version                                           | 5.5.56-MariaDB   |
| version_comment                                   | MariaDB Server   |
| version_compile_machine                           | x86_64           |
| version_compile_os                                | Linux            |
| wait_timeout                                      | 28800            |
+---------------------------------------------------+------------------+
""".strip()


def test_odbc_ini():
    res = MysqladminVars(context_wrap(INPUT_NORMAL))
    assert len(list(res.items())) == 14
    assert res.version_comment == 'MariaDB Server'
    assert res.datadir == '/var/lib/mysql/'
    assert res.auto_increment_increment == '1'
    assert 'abc' not in res
    assert res.get('abc', '233') == '233'
    assert res.get('init_file') == ''
    assert res.get('wait_what') is None
    assert res.get('wait_timeout') == '28800'
    assert res.get('Wait_Timeout') == '28800'
    assert res.getint('Wait_Timeout') == 28800
    assert res.getint('version_compile_machine') is None

    with pytest.raises(TypeError) as e_info:
        res.get('binlog_stmt_cache_size', 666)
    assert "Default value should be str type." in str(e_info.value)

    with pytest.raises(TypeError) as e_info:
        res.getint('binlog_stmt_cache_size', '666')
    assert "Default value should be int type." in str(e_info.value)


INPUT_EMPTY = """
+-------------------------------------------------+------------------+
| Variable_name                                   | Value            |
+-------------------------------------------------+------------------+
+-------------------------------------------------+------------------+
""".strip()

INPUT_FORAMT_WRONG = """
+-------------------------------------------------+------------------+
| Variable_name                                   | Value            |
+-------------------------------------------------+------------------+
| aria_block_size                                 | 1                |
| aria_checkpoint_interval                        | 30   |    23     |
+-------------------------------------------------+------------------+
""".strip()


def test_empty_mysqladmin_var():

    with pytest.raises(ParseException) as e_info:
        MysqladminVars(context_wrap(INPUT_EMPTY))
    assert "Empty or wrong content in table." in str(e_info.value)

    with pytest.raises(ParseException) as e_info:
        MysqladminVars(context_wrap(INPUT_FORAMT_WRONG))
    assert "Unparseable line in table." in str(e_info.value)
