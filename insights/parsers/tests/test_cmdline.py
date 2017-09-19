from insights.parsers.cmdline import CmdLine
from insights.tests import context_wrap

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


def test_cmdline():
    cmd_line = CmdLine(context_wrap(CMDLINE_V1))
    assert len(cmd_line.data) == 16
    assert cmd_line.get('ro') is None
    assert cmd_line.get('root') == ['/dev/mapper/vg_rootvg-lv_root']
    assert cmd_line.get('rd_LVM_LV') == ['vg_rootvg/lv_root', 'vg_rootvg/lv_swap']
    # Handle non-alphabet characters and extra spaces
    assert cmd_line['crashkernel'] == ['191M@0M']
    assert isinstance(cmd_line.get('audit'), list)
    assert cmd_line.get('audit') == [None, '1']

    cmd_line = CmdLine(context_wrap(CMDLINE_V2))
    assert cmd_line.get('audit') == ['1', '0', None, None]
