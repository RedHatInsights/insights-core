import doctest
import pytest

from insights.parsers import systemd_analyze
from insights.parsers import SkipException
from insights.tests import context_wrap


OUTPUT = """
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

OUTPUT_IN_MIN = """
1min 32.187s cloud-init-local.service
        1min cloud-config.service
      1.794s cloud-init.service
""".strip()


def test_output():
    output = systemd_analyze.SystemdAnalyzeBlame(context_wrap(OUTPUT))
    assert ('cloud-init-local.service' in output) is True

    # Test time(seconds)
    assert output.get('cloud-init.service', 0) == 1.304

    with pytest.raises(SkipException):
        assert systemd_analyze.SystemdAnalyzeBlame(context_wrap("")) is None


def test_output_in_min():
    output = systemd_analyze.SystemdAnalyzeBlame(context_wrap(OUTPUT_IN_MIN))
    assert output.get('cloud-init-local.service', 0) == 92.187
    assert output.get('cloud-config.service', 0) == 60


def test_documentation():
    failed_count, tests = doctest.testmod(
        systemd_analyze,
        globs={'output': systemd_analyze.SystemdAnalyzeBlame(context_wrap(OUTPUT))}
    )
    assert failed_count == 0
