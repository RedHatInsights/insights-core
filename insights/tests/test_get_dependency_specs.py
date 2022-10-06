from insights import condition, rule, make_fail
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.up2date import Up2Date
from insights.parsers.messages import Messages
from insights.parsers.ps import PsAuxcww
from insights.parsers.virt_what import VirtWhat
from insights.parsers.date import Date
from insights.parsers.tags import Tags
from insights.parsers.lspci import LsPci, LsPciVmmkn
from insights.parsers.lsof import Lsof
from insights.parsers.lscpu import LsCPU
from insights.parsers.lsblk import LSBlock
from insights.parsers.ls_etc import LsEtc
from insights.parsers.ls_boot import LsBoot
from insights.parsers.ls_dev import LsDev
from insights.parsers.ls_disk import LsDisk
from insights.parsers.ls_tmp import LsTmp
from insights.parsers.ls_usr_bin import LsUsrBin
from insights.parsers.ls_var_log import LsVarLog
from insights.parsers.ls_var_tmp import LsVarTmp
from insights.parsers.ls_var_www_perms import LsVarWwwPerms
from insights.parsers.ls_var_run import LsVarRun
from insights.parsers.mount import Mount
from insights.parsers.lvm import LvmConfig, LvmConf
from insights.parsers.lsscsi import LsSCSI
from insights.parsers.uptime import Uptime
from insights.combiners.redhat_release import RedHatRelease
from insights.core.dr import get_dependency_specs


@condition(InstalledRpms, [Up2Date, PsAuxcww], optional=[Messages])
def condition_1(*args):
    return True


@condition(VirtWhat, Tags, RedHatRelease, optional=[Date, Uptime])
def condition_2(*args):
    return True


@condition(LsVarLog, [LsBoot, LsEtc])
def condition_3(*args):
    return True


@condition(LsVarWwwPerms, [LsDev, LsDisk], optional=[LsVarRun])
def condition_4(*args):
    return True


@condition([LsPci, LsPciVmmkn])
def condition_5(*args):
    return True


@condition([LvmConf, LvmConfig])
def condition_6(*args):
    return True


@condition(Mount, [LsTmp, LsVarTmp], optional=[LsUsrBin])
def condition_7(*args):
    return True


@rule(Lsof, condition_1, condition_2,
      [LsCPU, condition_3], [condition_4, LsSCSI], [condition_5, condition_6],
      optional=[LSBlock, condition_7])
def report(*args):
    return make_fail("HIT")


@condition(LsVarLog, [LsBoot, LsEtc])
def ABC(*args):
    return True


@condition([LsPci, ABC])
def DEF(*args):
    return True


@condition(LsPci, LsBoot, LsDisk)
def XYZ(*args):
    return True


def test_get_dependency_specs_1_level_requires_only():
    specs = get_dependency_specs(XYZ)
    assert sorted(specs) == ['ls_boot', 'ls_disk', 'lspci']


def test_get_dependency_specs_2_level():
    specs = get_dependency_specs(DEF)
    # [
    #     ('lspci', [('ls_etc', 'ls_boot'), 'ls_var_log'])
    # ]
    assert len([alo for alo in specs if isinstance(alo, tuple)]) == 1
    assert 'lspci' in specs[0]
    x, y = specs[0]
    if x == 'lspci':
        assert 'ls_var_log' in y
    else:
        assert 'ls_var_log' in x
        m, n = x
        if isinstance(m, tuple):
            t = m
        else:
            t = n
        assert all(i in t for i in ('ls_etc', 'ls_boot'))


def test_get_dependency_specs_complex():
    specs = get_dependency_specs(report)
    # [
    #     'installed_rpms',
    #     'tags',
    #     'lsof',
    #     'virt_what',
    #     ('redhat_release', 'uname'),
    #     ('ps_auxcww', 'up2date'),
    #     ('ls_cpu', ['ls_var_log', ('ls_boot', 'ls_etc')]),
    #     ('lsscsi', ['ls_var_tmp', ('ls_disk', 'ls_dev')]),
    #     (('lspci', 'lspci_vmmkn'), ('lvm_conf', 'lvmconfig'))
    # ]
    requires = ['installed_rpms', 'tags', 'lsof', 'virt_what']
    assert all(req in specs for req in requires) is True
    # It's difficult to check the details since the result would in different
    # order due to python versions.  Here we just check the number of the
    # `at_least_one` specs
    assert len([alo for alo in specs if isinstance(alo, tuple)]) == 5
