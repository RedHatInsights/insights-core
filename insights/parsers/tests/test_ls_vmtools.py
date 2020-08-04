from insights.parsers.ls_vmtools import LsVMTools
from insights.tests import context_wrap

LSVMTOOLS = """
lrwxrwxrwx. 1 root root 30 Jun 11 19:32 etc/rc.d/init.d/vmware-tools -> ../../vmware-tools/services.sh
""".strip()

LSVMTOOLS_NO = """
ls: cannot access 'etc/rc.d/init.d/vmware-tools': No such file or directory
""".strip()


def test_ls_boot():
    ls_vmtools = LsVMTools(context_wrap(LSVMTOOLS))
    assert 'vmware-tools' in ls_vmtools

    ls_vmtools = LsVMTools(context_wrap(LSVMTOOLS_NO))
    assert 'vmware-tools' not in ls_vmtools
