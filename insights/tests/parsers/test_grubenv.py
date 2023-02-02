import doctest

from insights.parsers import grubenv
from insights.tests import context_wrap
from insights.tests.parsers import skip_component_check


GRUBENV_WITH_TUNED_PARAMS = """
saved_entry=295e1ba1696e4fad9e062f096f92d147-4.18.0-305.el8.x86_64
kernelopts=root=/dev/mapper/root_vg-lv_root ro crashkernel=auto resume=/dev/mapper/root_vg-lv_swap rd.lvm.lv=root_vg/lv_root rd.lvm.lv=root_vg/lv_swap console=tty0 console=ttyS0,115200 
boot_success=0
boot_indeterminate=2
tuned_params=transparent_hugepages=never
tuned_initrd=
""".strip()  # noqa

GRUBENV_WITHOUT_TUNED_PARAMS = """
saved_entry=295e1ba1696e4fad9e062f096f92d147-4.18.0-305.el8.x86_64
kernelopts=root=/dev/mapper/root_vg-lv_root ro crashkernel=auto resume=/dev/mapper/root_vg-lv_swap rd.lvm.lv=root_vg/lv_root rd.lvm.lv=root_vg/lv_swap console=tty0 console=ttyS0,115200 
boot_success=0
boot_indeterminate=2
""".strip()  # noqa

GRUBENV_RHEL7 = """
saved_entry=Red Hat Enterprise Linux Server (3.10.0-1127.el7.x86_64) 7.8 (Maipo)
""".strip()  # noqa

GRUBEDITENVLIST_ERROR = """
grub2-editenv: error: invalid environment block.
""".strip()


def test_doc_examples():
    env = {
        'grubenv': grubenv.GrubEnv(context_wrap(GRUBENV_WITH_TUNED_PARAMS))
    }
    failed, total = doctest.testmod(grubenv, globs=env)
    assert failed == 0


def test_with_tuned_params():
    results = grubenv.GrubEnv(context_wrap(GRUBENV_WITH_TUNED_PARAMS))
    assert results is not None
    assert results.has_kernelopts
    assert results.has_tuned_params
    assert results.kernelopts == "root=/dev/mapper/root_vg-lv_root ro crashkernel=auto resume=/dev/mapper/root_vg-lv_swap rd.lvm.lv=root_vg/lv_root rd.lvm.lv=root_vg/lv_swap console=tty0 console=ttyS0,115200"  # noqa
    assert results.tuned_params == "transparent_hugepages=never"
    assert results['saved_entry'] == "295e1ba1696e4fad9e062f096f92d147-4.18.0-305.el8.x86_64"
    assert results['boot_success'] == "0"
    assert results['boot_indeterminate'] == "2"


def test_without_tuned_params():
    results = grubenv.GrubEnv(context_wrap(GRUBENV_WITHOUT_TUNED_PARAMS))
    assert results is not None
    assert results.has_kernelopts
    assert not results.has_tuned_params
    assert results.kernelopts == "root=/dev/mapper/root_vg-lv_root ro crashkernel=auto resume=/dev/mapper/root_vg-lv_swap rd.lvm.lv=root_vg/lv_root rd.lvm.lv=root_vg/lv_swap console=tty0 console=ttyS0,115200"  # noqa
    assert results.tuned_params == ""
    assert results['saved_entry'] == "295e1ba1696e4fad9e062f096f92d147-4.18.0-305.el8.x86_64"
    assert results['boot_success'] == "0"
    assert results['boot_indeterminate'] == "2"


def test_r7():
    results = grubenv.GrubEnv(context_wrap(GRUBENV_RHEL7))
    assert results is not None
    assert not results.has_kernelopts
    assert not results.has_tuned_params
    assert results.kernelopts == ""
    assert results.tuned_params == ""
    assert results['saved_entry'] == "Red Hat Enterprise Linux Server (3.10.0-1127.el7.x86_64) 7.8 (Maipo)"


def test_skip():
    skip_component_check(grubenv.GrubEnv, output_str="# test")
    skip_component_check(grubenv.GrubEnv)


def test_error():
    results = grubenv.GrubEnv(context_wrap(GRUBEDITENVLIST_ERROR))
    assert results is not None
    assert results.errors == ["grub2-editenv: error: invalid environment block."]
