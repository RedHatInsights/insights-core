from insights.tests import context_wrap
from insights.parsers.cpuinfo_max_freq import cpu_max_freq

cpuinfo_content = '3200000'


def test_cpu_max_freq():
    result = cpu_max_freq(context_wrap(cpuinfo_content))
    assert result == 3200000
