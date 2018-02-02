from insights.parsers.blkid import BlockIDInfo
from insights.tests import context_wrap

BLKID_INFO = """
/dev/sda1: UUID="3676157d-f2f5-465c-a4c3-3c2a52c8d3f4" TYPE="xfs"
/dev/sda2: UUID="UVTk76-UWOc-vk7s-galL-dxIP-4UXO-0jG4MH" TYPE="LVM2_member"
/dev/mapper/rhel_hp--dl160g8--3-root: UUID="11124c1d-990b-4277-9f74-c5a34eb2cd04" TYPE="xfs"
/dev/mapper/rhel_hp--dl160g8--3-swap: UUID="c7c45f2d-1d1b-4cf0-9d51-e2b0046682f8" TYPE="swap"
/dev/mapper/rhel_hp--dl160g8--3-home: UUID="c7116820-f2de-4aee-8ea6-0b23c6491598" TYPE="xfs"
/dev/mapper/rhel_hp--dl160g8--3-lv_test: UUID="d403bcbd-0eea-4bff-95b9-2237740f5c8b" TYPE="ext4"
/dev/cciss/c0d1p3: LABEL="/u02" UUID="004d0ca3-373f-4d44-a085-c19c47da8b5e" TYPE="ext3"
/dev/loop0: LABEL="Satellite-5.6.0 x86_64 Disc 0" TYPE="iso9660"
/dev/block/253:1: UUID="f8508c37-eeb1-4598-b084-5364d489031f" TYPE="ext2"
""".strip()

EXPECTED_RESULTS = [{'NAME': "/dev/sda1",
                     'UUID': "3676157d-f2f5-465c-a4c3-3c2a52c8d3f4",
                     'TYPE': "xfs"},
                    {'NAME': "/dev/sda2",
                     'UUID': "UVTk76-UWOc-vk7s-galL-dxIP-4UXO-0jG4MH",
                     'TYPE': "LVM2_member"},
                    {'NAME': "/dev/mapper/rhel_hp--dl160g8--3-root",
                     'UUID': "11124c1d-990b-4277-9f74-c5a34eb2cd04",
                     'TYPE': "xfs"},
                    {'NAME': "/dev/mapper/rhel_hp--dl160g8--3-swap",
                     'UUID': "c7c45f2d-1d1b-4cf0-9d51-e2b0046682f8",
                     'TYPE': "swap"},
                    {'NAME': "/dev/mapper/rhel_hp--dl160g8--3-home",
                     'UUID': "c7116820-f2de-4aee-8ea6-0b23c6491598",
                     'TYPE': "xfs"},
                    {'NAME': "/dev/mapper/rhel_hp--dl160g8--3-lv_test",
                     'UUID': "d403bcbd-0eea-4bff-95b9-2237740f5c8b",
                     'TYPE': "ext4"},
                    {'NAME': "/dev/block/253:1",
                     'UUID': "f8508c37-eeb1-4598-b084-5364d489031f",
                     'TYPE': "ext2"},
                    {'NAME': "/dev/cciss/c0d1p3",
                     'LABEL': "/u02",
                     'UUID': "004d0ca3-373f-4d44-a085-c19c47da8b5e",
                     'TYPE': "ext3"},
                    {'NAME': "/dev/loop0",
                     'LABEL': "Satellite-5.6.0 x86_64 Disc 0",
                     'TYPE': "iso9660"}]


class TestBLKID():
    def test_get_blkid_info(self):
        blkid_info = BlockIDInfo(context_wrap(BLKID_INFO))
        expected_list = dict((r['NAME'], r) for r in EXPECTED_RESULTS)
        assert len(blkid_info.data) == 9

        for result in blkid_info.data:
            assert result == expected_list[result['NAME']]
        ext4_only = blkid_info.filter_by_type("ext4")
        assert len(ext4_only) == 1
        assert ext4_only[0] == {'NAME': "/dev/mapper/rhel_hp--dl160g8--3-lv_test",
                                'UUID': "d403bcbd-0eea-4bff-95b9-2237740f5c8b",
                                'TYPE': "ext4"}
        xfs_only = blkid_info.filter_by_type("xfs")
        expected_list = dict((r['NAME'], r) for r in EXPECTED_RESULTS if r['TYPE'] == "xfs")
        assert len(xfs_only) == 3
        for result in xfs_only:
            assert result == expected_list[result['NAME']]
        ext2_only = blkid_info.filter_by_type("ext2")
        ext2_only[0]["NAME"] == "/dev/block/253:1"
