from insights.parsers import SkipException, ParseException
from insights.parsers import cmdline
from insights.parsers.cmdline import CmdLine
from insights.tests import context_wrap
import doctest
import pytest

CMDLINE_V1 = "ro root=/dev/mapper/vg_rootvg-lv_root rd_LVM_LV=vg_rootvg/lv_root" +\
    " rd_LVM_LV=vg_rootvg/lv_swap rd_NO_LUKS rd_NO_MD rd_NO_DM " +\
    "LANG=en_US.UTF-8 SYSFONT=latarcyrheb-sun16 KEYBOARDTYPE=pc KEYTABLE=us " +\
    "        crashkernel=191M@0M hugepagesz=1073741824 hugepages=50 rhgb quiet" +\
    " audit audit=1"

CMDLINE_V2 = "ro root=/dev/mapper/vg_rootvg-lv_root rd_LVM_LV=vg_rootvg/lv_root" +\
    " rd_LVM_LV=vg_rootvg/lv_swap rd_NO_LUKS rd_NO_MD rd_NO_DM " +\
    "LANG=en_US.UTF-8 SYSFONT=latarcyrheb-sun16 KEYBOARDTYPE=pc KEYTABLE=us " +\
    "        crashkernel=191M@0M hugepagesz=1073741824 hugepages=50 rhgb quiet" +\
    " audit=1 audit=0 audit audit"

CMDLINE_GRUB2 = "BOOT_IMAGE=/vmlinuz-3.10.0-327.36.3.el7.x86_64 root=/dev/system_vg/Root ro rd.lvm.lv=system_vg/Root crashkernel=auto rd.lvm.lv=system_vg/Swap rhgb quiet LANG=en_GB.utf8"
CMDLINE_GRUB2_EMPTY = ""
CMDLINE_GRUB2_AB = """
BOOT_IMAGE=/vmlinuz-3.10.0-327.36.3.el7.x86_64
root=/dev/system_vg/Root ro rd.lvm.lv=system_vg/Root crashkernel=auto
rd.lvm.lv=system_vg/Swap rhgb quiet LANG=en_GB.utf8
""".strip()


def test_cmdline_v1():
    cmd_line = CmdLine(context_wrap(CMDLINE_V1))
    assert cmd_line.get('ro') == [True]
    assert cmd_line.get('root') == ['/dev/mapper/vg_rootvg-lv_root']
    assert cmd_line.get('rd_LVM_LV') == ['vg_rootvg/lv_root', 'vg_rootvg/lv_swap']
    # Handle non-alphabet characters and extra spaces
    assert cmd_line['crashkernel'] == ['191M@0M']
    assert cmd_line.get('audit') == [True, '1']


def test_cmdline_v2():
    cmd_line = CmdLine(context_wrap(CMDLINE_V2))
    assert cmd_line.get('audit') == ['1', '0', True, True]
    assert cmd_line.cmdline == CMDLINE_V2


def test_cmdline_ab():
    with pytest.raises(SkipException):
        CmdLine(context_wrap(CMDLINE_GRUB2_EMPTY))

    with pytest.raises(ParseException) as ex:
        CmdLine(context_wrap(CMDLINE_GRUB2_AB))
    assert 'Invalid output:' in str(ex)


def test_doc_examples():
    env = {
            'cmd': CmdLine(context_wrap(CMDLINE_GRUB2)),
          }
    failed, total = doctest.testmod(cmdline, globs=env)
    assert failed == 0
