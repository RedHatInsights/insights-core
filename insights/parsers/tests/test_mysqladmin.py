import pytest
from insights.parsers import ParseException, SkipException
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


def test_mysqladmin_vars():
    res = MysqladminVars(context_wrap(INPUT_NORMAL))
    d = res.data
    assert len(list(d)) == 14
    assert d['version_comment'] == 'MariaDB Server'
    assert d['datadir'] == '/var/lib/mysql/'
    assert d['auto_increment_increment'] == '1'
    assert d.get('abc') is None
    assert res.get('abc', '233') == '233'
    assert res.get('init_file') == ''
    assert res.get('wait_what') is None
    assert res.get('wait_timeout') == '28800'
    assert res.getint('wait_timeout') == 28800
    assert res.getint('version_compile_machine') is None
    assert res.get('binlog_stmt_cache_size', '666') == '32768'

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
| version_compile_machine                          x86_64           |
| version_compile_machine                         | x86_64           |x
| old_password********                                     ********
| version_compile_machine                           | x86_64           |
+-------------------------------------------------+------------------+
""".strip()


def test_empty_mysqladmin_var():
    with pytest.raises(SkipException) as e_info:
        MysqladminVars(context_wrap(""))
    assert "Empty content." in str(e_info.value)


def test_wrong_mysqladmin_var():
    with pytest.raises(ParseException) as e_info:
        MysqladminVars(context_wrap(INPUT_EMPTY))
    assert "Variable_name" in str(e_info.value)


INPUT_STILL_PARSABLE_1 = """
+-------------------------------------------------+------------------+
| Variable_name                                   | Value            |
+-------------------------------------------------+------------------+
| aria_block_size                                 | 1                |
| aria_checkpoint_interval                        | 30   |    23     |
+-------------------------------------------------+------------------+
""".strip()

INPUT_STILL_PARSABLE_2 = """
+---------------------------------------------------+-------------------
| Variable_name                                     | Value            |
+---------------------------------------------------+------------------+
| aria_block_size                                   | 8192             |
| aria_checkpoint_interval                          | 30               |
| ft_boolean_syntax                                 | + -><()~*:""&|   |
| version_compile_machine                           | x86_64           |
| version_compile_os                                | Linux            |
+---------------------------------------------------+------------------+
""".strip()

INPUT_FORAMT_WRONG = """
+-------------------------------------------------+------------------+
| Variable_name                                   | Value            |
+-------------------------------------------------+------------------+
| aria_block_size                                 | 1                |
| version_compile_machine                          x86_64           |
| version_compile_machine                         | x86_64           |x
| old_password********                                     ********
| version_compile_machine                           | x86_64           |
+-------------------------------------------------+------------------+
""".strip()


def test_mysqladmin_still_parsable():
    res = MysqladminVars(context_wrap(INPUT_STILL_PARSABLE_1))
    d = res.data
    assert d['aria_checkpoint_interval'] == '30   |    23'

    res = MysqladminVars(context_wrap(INPUT_STILL_PARSABLE_2))
    d = res.data
    assert d['ft_boolean_syntax'] == '+ -><()~*:""&|'

    res = MysqladminVars(context_wrap(INPUT_FORAMT_WRONG))
    assert len(res.bad_lines) == 3
    assert res.bad_lines[1] == '| version_compile_machine                         | x86_64           |x'
