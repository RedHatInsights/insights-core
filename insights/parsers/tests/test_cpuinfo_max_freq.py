from insights.tests import context_wrap
from insights.parsers.cpuinfo_max_freq import cpu_max_freq

import warnings

cpuinfo_content = '3200000'


def test_cpu_max_freq():
    with warnings.catch_warnings(record=True) as w:
        result = cpu_max_freq(context_wrap(cpuinfo_content))
        assert result == 3200000

        # Check deprecation
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
