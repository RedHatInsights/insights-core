from insights.tests import context_wrap
from insights.parsers.cpu_vulns import CpuVulns
from insights.combiners import cpu_vulns_branch
from insights.combiners.cpu_vulns_branch import CpuVulnsBranch
import doctest
import os


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

BASE_PATH = '/sys/devices/system/cpu/vulnerabilities'

INPUT1 = context_wrap(INPUT_MELTDOWN, path=os.path.join(BASE_PATH, 'meltdown'))
INPUT2 = context_wrap(INPUT_SPECTRE_V1, path=os.path.join(BASE_PATH, 'spectre_v1'))
INPUT3 = context_wrap(INPUT_SPECTRE_V2, path=os.path.join(BASE_PATH, 'spectre_v2'))
INPUT4 = context_wrap(INPUT_SPEC_STORE_BYPASS, path=os.path.join(BASE_PATH, 'spec_store_bypass'))
INPUT5 = context_wrap(INPUT_SMT, path=os.path.join(BASE_PATH, 'l1tf'))
INPUT6 = context_wrap(INPUT_MDS, path=os.path.join(BASE_PATH, 'mds'))

def test_values_comb_meltdown():
    obj = CpuVulnsBranch(context_wrap(INPUT_MELTDOWN, path=os.path.join(BASE_PATH, 'meltdown')))
    assert obj.get_data == [{'meltdown': 'Mitigation: PTI'}]


def test_values_comb_spectre_v1():
    obj = CpuVulnsBranch(context_wrap(INPUT_SPECTRE_V1, path=os.path.join(BASE_PATH, 'spectre_v1')))
    assert obj.get_data == [{'spectre_v1': 'Mitigation: Load fences'}]


def test_values_comb_spectre_v2():
    obj = CpuVulnsBranch(context_wrap(INPUT_SPECTRE_V2, path=os.path.join(BASE_PATH, 'spectre_v2')))
    assert obj.get_data == [{'spectre_v2': 'Mitigation: Full generic retpoline, IBPB: conditional, IBRS_FW, STIBP: conditional, RSB filling'}]


def test_values_comb_spec_store_bypass():
    obj = CpuVulnsBranch(context_wrap(INPUT_SPEC_STORE_BYPASS, path=os.path.join(BASE_PATH, 'spec_store_bypass')))
    assert obj.get_data == [{'spec_store_bypass': 'Mitigation: Speculative Store Bypass disabled'}]


def test_values_comb_l1tf():
    obj = CpuVulnsBranch(context_wrap(INPUT_SMT, path=os.path.join(BASE_PATH, 'l1tf')))
    assert obj.get_data == [{'l1tf': 'Mitigation: PTE Inversion; VMX: conditional cache flushes, SMT vulnerable'}]


def test_values_comb_mds():
    obj = CpuVulnsBranch(context_wrap(INPUT_MDS, path=os.path.join(BASE_PATH, 'mds')))
    assert obj.get_data == [{'mds': 'Vulnerable: Clear CPU buffers attempted, no microcode; SMT vulnerable'}]


def test_values_integration():
    obj = CpuVulnsBranch(INPUT1, INPUT2, INPUT3, INPUT4, INPUT5, INPUT6)
    assert obj.get_data == [{'meltdown': 'Mitigation: PTI'}, {'spectre_v1': 'Mitigation: Load fences'}, {'spectre_v2': 'Mitigation: Full generic retpoline, IBPB: conditional, IBRS_FW, STIBP: conditional, RSB filling'}, {'spec_store_bypass': 'Mitigation: Speculative Store Bypass disabled'}, {'l1tf': 'Mitigation: PTE Inversion; VMX: conditional cache flushes, SMT vulnerable'}, {'mds': 'Vulnerable: Clear CPU buffers attempted, no microcode; SMT vulnerable'}]


def test_x86_enabled_documentation():
    """
    Here we test the examples in the documentation automatically using
    doctest.  We set up an environment which is similar to what a rule
    writer might see - a '/sys/devices/system/cpu/vulnerabilities/*' output
    that has been passed in as a parameter to the rule declaration.
    """

    parser1 = CpuVulns(INPUT1)
    parser2 = CpuVulns(INPUT2)
    parser3 = CpuVulns(INPUT3)
    parser4 = CpuVulns(INPUT4)
    parser5 = CpuVulns(INPUT5)
    parser6 = CpuVulns(INPUT6)

    env = {'cvb': CpuVulnsBranch([parser1, parser2, parser3, parser4, parser5, parser6])}
    failed, total = doctest.testmod(cpu_vulns_branch, globs=env)
    assert failed == 0
