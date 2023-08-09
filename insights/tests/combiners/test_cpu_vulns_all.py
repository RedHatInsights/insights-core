import doctest
import pytest

from insights.combiners import cpu_vulns_all
from insights.combiners.cpu_vulns_all import CpuVulnsAll
from insights.core.exceptions import SkipComponent
from insights.parsers.cpu_vulns import CpuVulns
from insights.tests import context_wrap

IMPUT_MELTDOWN_EMPTY = """
""".strip()

INPUT_MELTDOWN = """
Mitigation: PTI
""".strip()

INPUT_SPECTRE_V1 = """
Mitigation: Load fences
""".strip()

INPUT_SPECTRE_V2 = """
Mitigation: Full generic retpoline, IBPB: conditional, IBRS_FW, STIBP: conditional, RSB filling
""".strip()

INPUT_SPEC_STORE_BYPASS = """
Mitigation: Speculative Store Bypass disabled
""".strip()

INPUT_SMT = """
Mitigation: PTE Inversion; VMX: conditional cache flushes, SMT vulnerable
""".strip()

INPUT_MDS = """
Vulnerable: Clear CPU buffers attempted, no microcode; SMT vulnerable
""".strip()

INPUT0 = context_wrap(INPUT_MELTDOWN, path='')
INPUT1 = context_wrap(INPUT_MELTDOWN, path='/sys/devices/system/cpu/vulnerabilities/meltdown')
INPUT2 = context_wrap(INPUT_SPECTRE_V1, path='/sys/devices/system/cpu/vulnerabilities/spectre_v1')
INPUT3 = context_wrap(INPUT_SPECTRE_V2, path='/sys/devices/system/cpu/vulnerabilities/spectre_v2')
INPUT4 = context_wrap(INPUT_SPEC_STORE_BYPASS, path='/sys/devices/system/cpu/vulnerabilities/spec_store_bypass')
INPUT5 = context_wrap(INPUT_SMT, path='/sys/devices/system/cpu/vulnerabilities/l1tf')
INPUT6 = context_wrap(INPUT_MDS, path='/sys/devices/system/cpu/vulnerabilities/mds')

parser0 = CpuVulns(INPUT0)
parser1 = CpuVulns(INPUT1)
parser2 = CpuVulns(INPUT2)
parser3 = CpuVulns(INPUT3)
parser4 = CpuVulns(INPUT4)
parser5 = CpuVulns(INPUT5)
parser6 = CpuVulns(INPUT6)


def test_values_comb_meltdown():
    obj = CpuVulnsAll([parser1, parser2, parser3])
    assert 'meltdown' in obj
    assert obj == {'meltdown': 'Mitigation: PTI', 'spectre_v1': 'Mitigation: Load fences', 'spectre_v2': 'Mitigation: Full generic retpoline, IBPB: conditional, IBRS_FW, STIBP: conditional, RSB filling'}


def test_values_comb_spectre_v1():
    obj = CpuVulnsAll([parser1, parser2])
    assert 'spectre_v1' in obj
    assert obj == {'meltdown': 'Mitigation: PTI', 'spectre_v1': 'Mitigation: Load fences'}


def test_values_comb_spectre_v2():
    obj = CpuVulnsAll([parser1, parser3])
    assert 'spectre_v2' in obj
    assert obj == {'meltdown': 'Mitigation: PTI', 'spectre_v2': 'Mitigation: Full generic retpoline, IBPB: conditional, IBRS_FW, STIBP: conditional, RSB filling'}


def test_values_comb_spec_store_bypass():
    obj = CpuVulnsAll([parser1, parser4])
    assert 'spec_store_bypass' in obj
    assert obj == {'meltdown': 'Mitigation: PTI', 'spec_store_bypass': 'Mitigation: Speculative Store Bypass disabled'}


def test_values_comb_l1tf():
    obj = CpuVulnsAll([parser1, parser5])
    assert 'l1tf' in obj
    assert obj == {'meltdown': 'Mitigation: PTI', 'l1tf': 'Mitigation: PTE Inversion; VMX: conditional cache flushes, SMT vulnerable'}


def test_values_comb_mds():
    obj = CpuVulnsAll([parser6])
    assert 'mds' in obj
    assert obj == {'mds': 'Vulnerable: Clear CPU buffers attempted, no microcode; SMT vulnerable'}


def test_values_integration():
    obj = CpuVulnsAll([parser1, parser2, parser3, parser4, parser5, parser6])
    assert 'spectre_v1' and 'spec_store_bypass' in obj
    assert obj == {'meltdown': 'Mitigation: PTI', 'spectre_v1': 'Mitigation: Load fences', 'spectre_v2': 'Mitigation: Full generic retpoline, IBPB: conditional, IBRS_FW, STIBP: conditional, RSB filling', 'spec_store_bypass': 'Mitigation: Speculative Store Bypass disabled', 'l1tf': 'Mitigation: PTE Inversion; VMX: conditional cache flushes, SMT vulnerable', 'mds': 'Vulnerable: Clear CPU buffers attempted, no microcode; SMT vulnerable'}


def test_values_exp():
    with pytest.raises(SkipComponent) as pe:
        CpuVulnsAll([parser0])
    assert "Not available data" in str(pe)


def test_x86_enabled_documentation():
    """
    Here we test the examples in the documentation automatically using
    doctest.  We set up an environment which is similar to what a rule
    writer might see - a '/sys/devices/system/cpu/vulnerabilities/*' output
    that has been passed in as a parameter to the rule declaration.
    """

    parser1 = CpuVulns(INPUT1)
    parser2 = CpuVulns(INPUT2)
    env = {'cvb': CpuVulnsAll([parser1, parser2])}
    failed, total = doctest.testmod(cpu_vulns_all, globs=env)
    assert failed == 0
