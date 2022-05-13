import doctest
import pytest
from insights.parsers import cgroups
from insights.parsers.cgroups import Cgroups
from insights.tests import context_wrap

cgroups_content = """
#subsys_name	hierarchy	num_cgroups	enabled
cpuset	10	48	1
cpu	2	232	1
cpuacct	2	232	1
memory	5	232	1
devices	6	232	1
freezer	3	48	1
net_cls	4	48	1
blkio	9	232	1
perf_event	8	48	1
hugetlb	11	48	1
pids	7	232	1
net_prio	4	48	1
""".strip()


def test_cgroups():
    context = context_wrap(cgroups_content)
    i_cgroups = Cgroups(context)
    assert i_cgroups.get_num_cgroups("memory") == 232
    assert i_cgroups.is_subsys_enabled("memory") is True
    assert i_cgroups.subsystems["memory"]["enabled"] == "1"
    with pytest.raises(KeyError) as ke:
        i_cgroups.get_num_cgroups("Wrong_memory")
    assert "wrong subsys_name" in str(ke)


def test_cgroup_documentation():
    env = {
        'i_cgroups': Cgroups(context_wrap(cgroups_content))
    }
    failed, total = doctest.testmod(cgroups, globs=env)
    assert failed == 0
