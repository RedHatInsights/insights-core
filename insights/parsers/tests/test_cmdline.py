from insights.parsers.cmdline import CmdLine
from insights.tests import context_wrap

CMDLINE = "ro root=/dev/mapper/vg_rootvg-lv_root rd_LVM_LV=vg_rootvg/lv_root" +\
    " rd_LVM_LV=vg_rootvg/lv_swap rd_NO_LUKS rd_NO_MD rd_NO_DM " +\
    "LANG=en_US.UTF-8 SYSFONT=latarcyrheb-sun16 KEYBOARDTYPE=pc KEYTABLE=us " +\
    "        crashkernel=191M@0M hugepagesz=1073741824 hugepages=50 rhgb quiet"


class TestCmdLine():
    def test_cmdline(self):
        cmd_line = CmdLine(context_wrap(CMDLINE))
        assert len(cmd_line.data) == 15
        assert cmd_line.data.get('ro') is None
        assert cmd_line.data.get('root') == ['/dev/mapper/vg_rootvg-lv_root']
        assert cmd_line.data.get('rd_LVM_LV') == ['vg_rootvg/lv_root', 'vg_rootvg/lv_swap']
        # Handle non-alphabet characters and extra spaces
        assert cmd_line.data['crashkernel'] == ['191M@0M']
