"""
CpuVulnsBranch - combiner for cpu vulnerabilities:
==================================================

cpu vulnerabilities includes:
    * CpuVulnsBranch - file /sys/devices/system/cpu/vulnerabilities/*

Examples:
    >>> type(cvb)
    <class 'insights.combiners.cpu_vulns_branch.CpuVulnsBranch'>
    >>> cvb.get_data
    [{'meltdown': 'Mitigation: PTI'}, {'spectre_v1': 'Mitigation: Load fences'}, {'spectre_v2': 'Mitigation: Full generic retpoline, IBPB: conditional, IBRS_FW, STIBP: conditional, RSB filling'}, {'spec_store_bypass': 'Mitigation: Speculative Store Bypass disabled'}, {'l1tf': 'Mitigation: PTE Inversion; VMX: conditional cache flushes, SMT vulnerable'}, {'mds': 'Vulnerable: Clear CPU buffers attempted, no microcode; SMT vulnerable'}]

    Attributes:
        path (str)   : The file name of /sys/devices/system/cpu/vulnerabilities/FILE_1
        context (str): The content of /sys/devices/system/cpu/vulnerabilities/FILE_1
"""

from insights.core.plugins import combiner
from insights.parsers.cpu_vulns import CpuVulns
import os


@combiner(CpuVulns)
class CpuVulnsBranch(object):
    """
    This combiner provides an interface to CPU vulnerabilities parsers.
    """

    def __init__(self, *args, **kwargs):
        self.args = args

    @property
    def get_data(self):
        flist = []
        for arg in self.args:
            fdict = {}
            if arg.path and arg.content[0]:
                fname = os.path.basename(arg.path)
                fdict[fname] = arg.content[0]
                flist.append(fdict)
        return flist
