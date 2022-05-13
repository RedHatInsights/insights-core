import doctest
import pytest

from insights.parsers import systemd_analyze
from insights.parsers import SkipException
from insights.tests import context_wrap


OUTPUT = """
1y 1month 2w 6d 1h 33min 53.782s dev-sdy.device
2month 3w 4d 7h 10min 17.082s dev-sdm.device
1w 5d 2h 8min 12.802s dev-sdw.device
3d 8h 57min 30.859s dev-sdd.device
2h 56min 26.721s dev-mapper-vg_root\x2dlv_root.device
5min 230ms splunk.service
33.080s cloud-init-local.service
32.423s unbound-anchor.service
 2.773s kdump.service
 1.699s dnf-makecache.service
 1.304s cloud-init.service
 1.073s initrd-switch-root.service
  939ms cloud-config.service
  872ms tuned.service
  770ms cloud-final.service
""".strip()


def test_output():
    output = systemd_analyze.SystemdAnalyzeBlame(context_wrap(OUTPUT))
    assert ('cloud-init-local.service' in output) is True

    # Test time(seconds)
    assert output.get('tuned.service', 0) == 0.872
    assert output.get('cloud-init.service', 0) == 1.304
    assert output.get('splunk.service', 0) == 300.23
    assert output.get('dev-sdd.device', 0) == 291450.859
    assert output.get('dev-sdy.device', 0) == 35921033.782

    with pytest.raises(SkipException):
        assert systemd_analyze.SystemdAnalyzeBlame(context_wrap("")) is None


def test_documentation():
    failed_count, tests = doctest.testmod(
        systemd_analyze,
        globs={'output': systemd_analyze.SystemdAnalyzeBlame(context_wrap(OUTPUT))}
    )
    assert failed_count == 0
