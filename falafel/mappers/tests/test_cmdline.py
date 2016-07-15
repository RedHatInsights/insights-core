from falafel.mappers import cmdline
from falafel.tests import context_wrap

CMDLINE = """
ro root=/dev/mapper/vg_rootvg-lv_root rd_LVM_LV=vg_rootvg/lv_root rd_LVM_LV=vg_rootvg/lv_swap rd_NO_LUKS rd_NO_MD rd_NO_DM LANG=en_US.UTF-8 SYSFONT=latarcyrheb-sun16 KEYBOARDTYPE=pc KEYTABLE=us crashkernel=191M@0M hugepagesz=1073741824 hugepages=50 rhgb quiet\n

""".strip()


class TestCmdLine():
    def test_cmdline(self):
        cmd_line = cmdline.get_cmdline(context_wrap(CMDLINE))
        assert len(cmd_line) == 15
        assert cmd_line.get('ro') == None
        assert cmd_line.get('root') == ['/dev/mapper/vg_rootvg-lv_root']
        assert cmd_line.get('rd_LVM_LV') == ['vg_rootvg/lv_root', 'vg_rootvg/lv_swap']