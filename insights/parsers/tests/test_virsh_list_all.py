import doctest

from insights.parsers import virsh_list_all
from insights.tests import context_wrap


BLANK = """
""".strip()

NO_RESULT = """
 Id    Name                           State
----------------------------------------------------
""".strip()

OUTPUT = """
 Id    Name                           State
----------------------------------------------------
 2     rhel7.4                        running
 4     rhel7.0                        paused
 -     centos6.8-router               shut off
 -     cfme-5.7.13                    shut off
 -     cfme-rhos-5.9.0.15             shut off
 -     fedora-24-kernel               shut off
 -     fedora-saio_fedoraSaio         shut off
 -     fedora24-misc                  shut off
 -     freebsd11.0                    shut off
 -     guixSD                         shut off
 -     miq-gap-1                      shut off
 -     rhel7.2                        shut off
 -     RHOSP10                        shut off
""".strip()


def test_virsh_output():
    output = virsh_list_all.VirshListAll(context_wrap(OUTPUT))
    assert len(output.search(state='shut off')) == 11
    assert len(output.search(id=None)) == 11
    assert len(output.search(id=2)) == 1
    assert output.search(name='rhel7.4') == [{'state': 'running', 'id': 2, 'name': 'rhel7.4'}]
    assert output.get_vm_state('rhel7.0') == 'paused'
    assert output.get_vm_state('rhel9.0') is None
    assert ('cfme' in output) is False
    assert ('cfme-5.7.13' in output) is True
    assert output.get_vm_state("RHOSP10") == "shut off"


def test_virsh_output_no_vms():
    output = virsh_list_all.VirshListAll(context_wrap(NO_RESULT))
    assert output.fields == []
    assert output.cols == []
    assert output.keywords == []
    assert output.get_vm_state('NORHEL') is None


def test_virsh_output_blank():
    output = virsh_list_all.VirshListAll(context_wrap(BLANK))
    assert output.fields == []
    assert output.cols == []
    assert output.keywords == []
    assert output.get_vm_state('NORHEL') is None


def test_virsh_list_all_documentation():
    failed_count, tests = doctest.testmod(
        virsh_list_all,
        globs={'output': virsh_list_all.VirshListAll(context_wrap(OUTPUT))}
    )
    assert failed_count == 0
