import doctest
from insights.parsers import mssql_conf
from insights.tests import context_wrap

MSSQL_CONF = """
[sqlagent]
enabled = false

[EULA]
accepteula = Y

[memory]
memorylimitmb = 3328
""".strip()


def test_mssql_conf():
    conf = mssql_conf.MsSQLConf(context_wrap(MSSQL_CONF))
    assert conf.has_option('memory', 'memorylimitmb') is True
    assert conf.get('memory', 'memorylimitmb') == '3328'


def test_documentation():
    env = {'conf': mssql_conf.MsSQLConf(context_wrap(MSSQL_CONF))}
    failed_count, tests = doctest.testmod(mssql_conf, globs=env)
    assert failed_count == 0
