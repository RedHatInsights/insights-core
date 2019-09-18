from insights.parsers import SkipException
from insights.parsers import cpu_vulns
from insights.parsers.cpu_vulns import CpuVulnsSpectreV2
from insights.tests import context_wrap
import pytest
import doctest


INPUT_SPECTRE_V2_RHEL_7 = """
Mitigation: Full generic retpoline, IBPB: conditional, IBRS_FW, STIBP: conditional, RSB filling
""".strip()

INPUT_SPECTRE_V2_RHEL_6 = """
Mitigation: IBRS (kernel)
""".strip()


def test_cpu_vulns_spectre_v2_rhel7():
    spectre = CpuVulnsSpectreV2(context_wrap(INPUT_SPECTRE_V2_RHEL_7))
    assert spectre.value == INPUT_SPECTRE_V2_RHEL_7


def test_cpu_vulns_spectre_v2_rhel6():
    spectre = CpuVulnsSpectreV2(context_wrap(INPUT_SPECTRE_V2_RHEL_6))
    assert spectre.value == INPUT_SPECTRE_V2_RHEL_6


def test_cpu_vulns_spectre_v2_documentation():
    """
    Here we test the examples in the documentation automatically using doctest.
    We set up an environment which is similar to what a rule writer might see -
    a '/sys/devices/system/cpu/vulnerabilities/spectre_v2' output that has been
    passed in as a parameter to the rule declaration.
    """
    env = {'obj': CpuVulnsSpectreV2(context_wrap(INPUT_SPECTRE_V2_RHEL_7))}
    failed, total = doctest.testmod(cpu_vulns, globs=env)
    assert failed == 0


def test_cpu_vulns_spectre_v2_exp():
    """
    Here test the examples cause expections
    """
    with pytest.raises(SkipException) as sc1:
        CpuVulnsSpectreV2(context_wrap(""))
    assert "Input content is empty" in str(sc1)
