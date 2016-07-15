from falafel.mappers import dumpe2fs_h
from falafel.tests import context_wrap

DUMPE2FS = """
dumpe2fs 1.41.12 (17-May-2010)
Filesystem volume name:   <none>
Last mounted on:          /usr
Filesystem UUID:          1b332c5d-2410-4934-9118-466f8a14841f
Filesystem magic number:  0xEF53
Filesystem revision #:    1 (dynamic)
Filesystem features:      has_journal ext_attr resize_inode dir_index filetype needs_recovery extent flex_bg sparse_super large_file huge_file uninit_bg dir_nlink extra_isize
Filesystem flags:         signed_directory_hash
Default mount options:    user_xattr acl journal_data_writeback

""".strip()

PATH = "sos_commands/filesys/dumpe2fs_-h_.dev.mapper.vg_spcdrhellb01-lv_usr"


class TestDumpe2fs():
    def test_dumpe2fs(self):
        dumpe2fs_dict = dumpe2fs_h.get_dumpe2fs_output(context_wrap(DUMPE2FS, path=PATH))
        assert dumpe2fs_dict.has_key("/dev/mapper/vg_spcdrhellb01-lv_usr")
        assert dumpe2fs_dict.get("/dev/mapper/vg_spcdrhellb01-lv_usr").get("Filesystem features") == ['has_journal', 'ext_attr', 'resize_inode', 'dir_index', 'filetype', 'needs_recovery', 'extent', 'flex_bg', 'sparse_super', 'large_file', 'huge_file', 'uninit_bg', 'dir_nlink', 'extra_isize']
        assert dumpe2fs_dict.get("/dev/mapper/vg_spcdrhellb01-lv_usr").get("Default mount options") == ['user_xattr', 'acl', 'journal_data_writeback']
        assert dumpe2fs_dict == {'/dev/mapper/vg_spcdrhellb01-lv_usr': {'Filesystem magic number': '0xEF53', 'Filesystem flags': 'signed_directory_hash', 'Filesystem revision #': '1 (dynamic)', 'Default mount options': ['user_xattr', 'acl', 'journal_data_writeback'], 'Last mounted on': '/usr', 'Filesystem UUID': '1b332c5d-2410-4934-9118-466f8a14841f', 'Filesystem volume name': '<none>', 'Filesystem features': ['has_journal', 'ext_attr', 'resize_inode', 'dir_index', 'filetype', 'needs_recovery', 'extent', 'flex_bg', 'sparse_super', 'large_file', 'huge_file', 'uninit_bg', 'dir_nlink', 'extra_isize']}}

