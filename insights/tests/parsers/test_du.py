import doctest
import pytest

from insights.core.exceptions import ContentException, ParseException, SkipComponent
from insights.parsers import du
from insights.parsers.du import DiskUsage
from insights.tests import context_wrap

# du -s /var/lib/pgsql
DU_VAR_LIB = """
186724	/var/lib/pgsql
""".strip()

# du -s /var/lib/*
DU_VAR_LIB_STAR = """
56	/var/lib/alternatives
4	/var/lib/logrotate
5492	/var/lib/mlocate
20	/var/lib/NetworkManager
186484	/var/lib/pgsql
856	/var/lib/rhsm
110712	/var/lib/rpm
4	/var/lib/rsyslog
64	/var/lib/systemd
15200	/var/lib/yum
""".strip()

# du -sh / containing only error lines
DU_ACCESS_ERROR = """
/bin/du: cannot access '/proc/17405/task/17405/fd/4': No such file or directory
/bin/du: cannot access '/proc/17405/task/17405/fdinfo/4': No such file or directory
""".strip()

# du -s / containing error lines and a valid value
DU_ACCESS_ERROR_OKAY = """
/bin/du: cannot access '/proc/17405/task/17405/fd/4': No such file or directory
5904560	/
""".strip()

# Valid output with spaces in path
DU_SPACES = """
102400	/mnt/abc xyz
""".strip()

# du -a inside a directory
DU_RELATIVE = """
1652	./messages
1652	.
"""

# du --blocks=4K , 4k blocks but no suffix unit
DU_4K_VAR_LOG = """
3	/var/log/tuned
3969	/var/log/rhsm
85	/var/log/httpd
3	/var/log/squid
""".strip()

# du -sh / containing only one error line
# CommandParser will throw ContentException as
# this contains single line with "No such file or directory"
DU_ACCESS_ERROR_SINGLE = """
/bin/du: cannot access '/proc/17405/task/17405/fd/4': No such file or directory
""".strip()

# 1M Blocks, Parser only supports integer values without unit suffix
DU_M_VAR_LOG = """
1M	/var/log/tuned
144M	/var/log/rhsm
26M	/var/log/httpd
5M	/var/log/squid
""".strip()

# du -h /var/log throwing exception
DU_H = """
12K	/var/log/tuned
144M	/var/log/rhsm
26M	/var/log/httpd
4.2M	/var/log/squid
""".strip()

DU_INVALID_1 = """
20	/var/lib/NetworkManager
110712
""".strip()

DU_INVALID_2 = """
2A	/var/lib/NetworkManager
""".strip()


def test_du():
    du = DiskUsage(context_wrap(DU_VAR_LIB))
    assert len(du) == 1
    assert '/var/lib/pgsql' in du
    assert du.get('/var/lib/pgsql') == 186724
    assert '/var/some/fake' not in du
    assert du.get('/Fake') is None
    assert du == {'/var/lib/pgsql': 186724}

    du = DiskUsage(context_wrap(DU_VAR_LIB_STAR))
    assert len(du) == 10
    assert '/var/lib/rpm' in du
    assert du.get('/var/lib/rpm') == 110712
    assert du == {'/var/lib/alternatives': 56, '/var/lib/logrotate': 4, '/var/lib/mlocate': 5492, '/var/lib/NetworkManager': 20, '/var/lib/pgsql': 186484, '/var/lib/rhsm': 856, '/var/lib/rpm': 110712, '/var/lib/rsyslog': 4, '/var/lib/systemd': 64, '/var/lib/yum': 15200}

    du = DiskUsage(context_wrap(DU_ACCESS_ERROR_OKAY))
    assert len(du) == 1
    assert '/' in du
    assert du.get('/') == 5904560

    du = DiskUsage(context_wrap(DU_SPACES))
    assert du.get('/mnt/abc xyz') == 102400
    assert du == {'/mnt/abc xyz': 102400}

    du = DiskUsage(context_wrap(DU_4K_VAR_LOG))
    assert len(du) == 4
    assert '/var/log/httpd' in du
    assert du.get('/var/log/httpd') == 85


def test_du_bad():

    with pytest.raises(SkipComponent) as exc:
        DiskUsage(context_wrap(DU_ACCESS_ERROR))
    assert 'No data parsed' in str(exc)

    with pytest.raises(ParseException) as exc:
        DiskUsage(context_wrap(DU_RELATIVE))
    assert 'Relative paths not supported' in str(exc)

    with pytest.raises(ContentException) as exc:
        DiskUsage(context_wrap(DU_ACCESS_ERROR_SINGLE))
    assert 'No such file or directory' in str(exc)

    with pytest.raises(ParseException) as exc:
        DiskUsage(context_wrap(DU_M_VAR_LOG))
    assert 'Could not parse line' in str(exc)

    with pytest.raises(ParseException) as exc:
        DiskUsage(context_wrap(DU_H))
    assert 'Could not parse line' in str(exc)

    with pytest.raises(ParseException) as exc:
        DiskUsage(context_wrap(DU_INVALID_1))
    assert 'Could not parse line' in str(exc)

    with pytest.raises(ParseException) as exc:
        DiskUsage(context_wrap(DU_INVALID_2))
    assert 'Could not parse line' in str(exc)


def test_du_doc_examples():
    env = {'disk_usage': DiskUsage(context_wrap(DU_VAR_LIB_STAR))}
    failed, total = doctest.testmod(du, globs=env)
    assert failed == 0
