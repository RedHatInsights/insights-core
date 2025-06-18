from insights import condition, rule, make_fail
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.uname import Uname
from insights.parsers.redhat_release import RedhatRelease
from insights.parsers.messages import Messages
from insights.parsers.ps import PsAuxcww, PsAux, PsAuxww, PsEf, PsEoCmd
from insights.parsers.virt_what import VirtWhat
from insights.parsers.date import Date, DateUTC
from insights.parsers.client_metadata import Tags
from insights.parsers.lspci import LsPci, LsPciVmmkn
from insights.parsers.lsof import Lsof
from insights.parsers.lscpu import LsCPU
from insights.parsers.lsblk import LSBlock
from insights.parsers.ls_boot import LsBoot
from insights.parsers.dmidecode import DMIDecode
from insights.parsers.os_release import OsRelease
from insights.parsers.mount import Mount
from insights.parsers.lvm import LvmConfig, LvmConf
from insights.parsers.lsscsi import LsSCSI
from insights.parsers.uptime import Uptime
from insights.parsers.dmesg import DmesgLineList
from insights.combiners.redhat_release import RedHatRelease
from insights.core.dr import get_dependency_specs


@condition(InstalledRpms, [PsAuxcww], optional=[Messages])
def condition_01(*args):
    return True


@condition(VirtWhat, Tags, RedHatRelease, optional=[Date, Uptime])
def condition_02(*args):
    return True


@condition(PsAux, [LsBoot, PsAuxww])
def condition_03(*args):
    return True


@condition(PsEf, [DMIDecode], optional=[PsEoCmd])
def condition_04(*args):
    return True


@condition([LsPci, LsPciVmmkn])
def condition_05(*args):
    return True


@condition([LvmConf, LvmConfig])
def condition_06(*args):
    return True


@condition(Mount, [OsRelease, PsEoCmd], optional=[DateUTC])
def condition_07(*args):
    return True


@rule(
    Lsof,
    condition_01,
    condition_02,
    [LsCPU, condition_03],
    [condition_04, LsSCSI],
    [condition_05, condition_06],
    optional=[LSBlock, condition_07],
)
def report_01(*args):
    return make_fail("HIT")


@condition(PsAux, [LsBoot, DmesgLineList])
def condition_11(*args):
    return True


@condition([LsPci, condition_11])
def condition_12(*args):
    return True


@condition(LsPci, LsBoot, DMIDecode)
def report_11(*args):
    return True


@condition(PsAuxcww, PsAux, [Uname, RedhatRelease], [LsPci, condition_11])
def condition_21(*args):
    return True


@condition(RedHatRelease, PsAux, condition_12, condition_21)
def report_21(*args):
    return True


def test_get_dependency_specs_1_level_requires_only():
    specs = get_dependency_specs(report_11)
    assert sorted(specs) == ['dmidecode', 'ls_boot', 'lspci']


def test_get_dependency_specs_2_level():
    specs = get_dependency_specs(condition_12)
    # [
    #     ('lspci', [('ps_auxww', 'ls_boot'), 'ps_aux'])
    # ]
    assert len([alo for alo in specs if isinstance(alo, tuple)]) == 1
    assert 'lspci' in specs[0]
    x, y = specs[0]
    if x == 'lspci':
        assert 'ps_aux' in y
    else:
        assert 'ps_aux' in x
        m, n = x
        if isinstance(m, tuple):
            t = m
        else:
            t = n
        assert all(i in t for i in ('ps_auxww', 'ls_boot'))


def test_get_dependency_specs_complex():
    specs = get_dependency_specs(report_01)
    # [
    #     'installed_rpms',
    #     'tags',
    #     'lsof',
    #     'virt_what',
    #     ('redhat_release', 'uname'),
    #     ('ps_auxcww', 'up2date'),
    #     ('ls_cpu', ['ps_aux', ('ls_boot', 'ps_auxww')]),
    #     ('lsscsi', ['ps_aux', ('dmidecode', 'ls_sys_firmware')]),
    #     (('lspci', 'lspci_vmmkn'), ('lvm_conf', 'lvmconfig'))
    # ]
    requires = ['installed_rpms', 'tags', 'lsof', 'virt_what']
    assert all(req in specs for req in requires) is True
    # It's difficult to check the details since the result would in different
    # order due to python versions.  Here we just check the number of the
    # `at_least_one` specs
    assert len([alo for alo in specs if isinstance(alo, tuple)]) == 5


def test_get_dependency_specs_duplicate():
    specs = get_dependency_specs(report_21)
    # [
    #     ('uname', 'redhat_release'),
    #     'ps_auxcww',
    #     'ps_aux',
    #     ('ls_pci', ['ps_aux', ('ls_boot', 'ps_auxww')])
    # ]
    # There is only one such item in the result
    assert ('uname', 'redhat_release') in specs
    specs.remove(('uname', 'redhat_release'))
    assert ('uname', 'redhat_release') not in specs

    assert 'ps_aux' in specs
    specs.remove('ps_aux')
    assert 'ps_aux' not in specs
