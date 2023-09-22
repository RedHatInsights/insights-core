"""
``test dumpe2fs_h``
===================
"""
from insights.parsers import dumpe2fs_h
from insights.tests import context_wrap

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


def test_dumpe2fs():
    dumpe2fs_obj = dumpe2fs_h.DumpE2fs(context_wrap(DUMPE2FS, path=PATH))
    assert dumpe2fs_obj.dev_name == '/dev/mapper/vg_spcdrhellb01-lv_usr'
    assert dumpe2fs_obj is not None
    assert type(dumpe2fs_obj['Filesystem features']) is list
    assert set(dumpe2fs_obj.get("Filesystem features")) == set([
        'has_journal', 'ext_attr', 'resize_inode', 'dir_index',
        'filetype', 'needs_recovery', 'extent', 'flex_bg', 'sparse_super',
        'large_file', 'huge_file', 'uninit_bg', 'dir_nlink', 'extra_isize'
    ])
    assert type(dumpe2fs_obj.get("Default mount options")) == list
    assert set(dumpe2fs_obj.get("Default mount options")) == \
        set(['user_xattr', 'acl', 'journal_data_writeback'])
    assert dumpe2fs_obj.get('Filesystem magic number') == '0xEF53'
    assert type(dumpe2fs_obj.get("Filesystem flags")) == list
    assert set(dumpe2fs_obj.get('Filesystem flags')) == set(['signed_directory_hash'])
    assert dumpe2fs_obj.get('Filesystem revision #') == '1 (dynamic)'
    assert dumpe2fs_obj.get('Last mounted on') == '/usr'
    assert dumpe2fs_obj.get('Filesystem UUID') == '1b332c5d-2410-4934-9118-466f8a14841f'
    assert dumpe2fs_obj.get('Filesystem volume name') == '<none>'
