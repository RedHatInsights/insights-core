from insights.parsers import ls_edac_mc
from insights.parsers.ls_edac_mc import LsEdacMC
from insights.tests import context_wrap
import doctest

LS_EDAC_MC = """
/sys/devices/system/edac/mc:
total 37592
drwxr-xr-x. 3 0 0 0 Jan 10 10:33 .
drwxr-xr-x. 3 0 0 0 Jan 10 10:33 ..
drwxr-xr-x. 2 0 0 0 Jan 10 10:33 power
drwxr-xr-x. 2 0 0 0 Jan 10 10:33 mc0
drwxr-xr-x. 2 0 0 0 Jan 10 10:33 mc1
drwxr-xr-x. 2 0 0 0 Jan 10 10:33 mc2
"""


def test_ls_edac_mc():
    ls_edac_mc = LsEdacMC(context_wrap(LS_EDAC_MC))
    assert '/sys/devices/system/edac/mc' in ls_edac_mc
    assert ls_edac_mc.dirs_of('/sys/devices/system/edac/mc') == ['.', '..', 'power', 'mc0', 'mc1', 'mc2']


def test_ls_etc_documentation():
    failed_count, tests = doctest.testmod(
        ls_edac_mc,
        globs={'ls_edac_mc': ls_edac_mc.LsEdacMC(context_wrap(LS_EDAC_MC))}
    )
    assert failed_count == 0
