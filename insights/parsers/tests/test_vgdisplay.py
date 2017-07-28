from insights.parsers import vgdisplay
from insights.tests import context_wrap


VGDISPLAY = """
Couldn't find device with uuid VVLmw8-e2AA-ECfW-wDPl-Vnaa-0wW1-utv7tV.
  There are 1 physical volumes missing.
    Couldn't find device with uuid VVLmw8-e2AA-ECfW-wDPl-Vnaa-0wW1-utv7tV.
  There are 1 physical volumes missing.
  --- Volume group ---
  VG Name               rhel_hp-dl160g8-3
  Format                lvm2
  System ID
  Metadata Areas        1
  Metadata Sequence No  5
  VG Access             read/write
  Total PE              119109
  Alloc PE / Size       119098 / 465.23 GiB
  Free  PE / Size       11 / 44.00 MiB
  VG UUID               by0Dl3-0lpB-MxEz-f6GO-9LYO-YRAQ-GufNZD

  VG Name               rhel_hp-dl260g7-4
  Format                lvm2
  System ID
  VG Access             read/write
  Alloc PE / Size       119098 / 465.23 GiB
  Free  PE / Size       11 / 44.00 MiB
  VG UUID               by0Dl3-0lpB-MxEz-f6GO-9LYO-YRAQ-GufNZN
""".strip()

VGDISPLAY_VV = """
      Setting activation/monitoring to 1
      Setting global/locking_type to 1
      Setting global/wait_for_locks to 1
      File-based locking selected.
      Setting global/prioritise_write_locks to 1
      Setting global/locking_dir to /run/lock/lvm
      Setting global/use_lvmlockd to 0
      Setting response to OK
      Setting token to filter:3239235440
      Setting daemon_pid to 856
      Setting response to OK
      Setting global_disable to 0
      Setting response to OK
      Setting response to OK
      Setting response to OK
      Setting name to RHEL7CSB
      report/output_format not found in config: defaulting to basic
      log/report_command_log not found in config: defaulting to 0
      Processing VG RHEL7CSB aeMrAJ-QkAe-llvW-oAoE-CWLF-MnUd-edD1tI
      Locking /run/lock/lvm/V_RHEL7CSB RB
      Reading VG RHEL7CSB aeMrAJQkAellvWoAoECWLFMnUdedD1tI
      Setting response to OK
      Setting response to OK
      Setting response to OK
      Setting name to RHEL7CSB
      Setting metadata/format to lvm2
      Setting id to EfWV9V-03CX-E6zc-JkMw-yQae-wdzp-Je1KUn
      Setting format to lvm2
      Setting device to 64768
      Setting dev_size to 970475520
      Setting label_sector to 1
      Setting ext_flags to 0
      Setting ext_version to 1
      Setting size to 1044480
      Setting start to 4096
      Setting ignore to 0
      Setting response to OK
      Setting response to OK
      Setting response to OK
      /dev/mapper/luks-96c66446-77fd-4431-9508-f6912bd84194: size is 970475520 sectors
      Process single VG RHEL7CSB
  --- Volume group ---
  VG Name               RHEL7CSB
  System ID
  Format                lvm2
  Metadata Areas        1
  Metadata Sequence No  13
  VG Access             read/write
  VG Status             resizable
  MAX LV                0
  Cur LV                7
  Open LV               6
  Max PV                0
  Cur PV                2
  Act PV                1
  VG Size               462.76 GiB
  PE Size               4.00 MiB
  Total PE              118466
  Alloc PE / Size       114430 / 446.99 GiB
  Free  PE / Size       4036 / 15.77 GiB
  VG UUID               aeMrAJ-QkAe-llvW-oAoE-CWLF-MnUd-edD1tI

      Adding RHEL7CSB/Home to the list of LVs to be processed.
      Adding RHEL7CSB/Root to the list of LVs to be processed.
      Adding RHEL7CSB/Swap to the list of LVs to be processed.
      Adding RHEL7CSB/VMs_lv to the list of LVs to be processed.
      Adding RHEL7CSB/NotBackedUp_lv to the list of LVs to be processed.
      Adding RHEL7CSB/ISOs_lv to the list of LVs to be processed.
      Adding RHEL7CSB/RHEL6-pg-pgsql-lv to the list of LVs to be processed.
      Processing LV Home in VG RHEL7CSB.
  --- Logical volume ---
      global/lvdisplay_shows_full_device_path not found in config: defaulting to 0
  LV Path                /dev/RHEL7CSB/Home
  LV Name                Home
  VG Name                RHEL7CSB
  LV UUID                IdRMoU-JorV-ChPg-F1zb-6np9-yc08-qxj08f
  LV Write Access        read/write
  LV Creation host, time localhost, 2015-04-16 00:02:47 +1000
  LV Status              available
  # open                 1
  LV Size                100.00 GiB
  Current LE             25600
  Segments               1
  Allocation             inherit
  Read ahead sectors     auto
  - currently set to     256
  Block device           253:3

      Processing LV Root in VG RHEL7CSB.
  --- Logical volume ---
      global/lvdisplay_shows_full_device_path not found in config: defaulting to 0
  LV Path                /dev/RHEL7CSB/Root
  LV Name                Root
  VG Name                RHEL7CSB
  LV UUID                lXBbNv-u1r6-qCo1-682K-w5hW-ED8A-Sl4gvf
  LV Write Access        read/write
  LV Creation host, time localhost, 2015-04-16 00:02:50 +1000
  LV Status              available
  # open                 1
  LV Size                29.30 GiB
  Current LE             7500
  Segments               1
  Allocation             inherit
  Read ahead sectors     auto
  - currently set to     256
  Block device           253:1

      Processing LV Swap in VG RHEL7CSB.
  --- Logical volume ---
      global/lvdisplay_shows_full_device_path not found in config: defaulting to 0
  LV Path                /dev/RHEL7CSB/Swap
  LV Name                Swap
  VG Name                RHEL7CSB
  LV UUID                R2ErFM-Rrql-L0tH-VIbm-F0Km-P7uW-4hk3rl
  LV Write Access        read/write
  LV Creation host, time localhost, 2015-04-15 14:02:52 +1000
  LV Status              available
  # open                 2
  LV Size                7.70 GiB
  Current LE             1970
  Segments               1
  Allocation             inherit
  Read ahead sectors     auto
  - currently set to     256
  Block device           253:2

      Processing LV VMs_lv in VG RHEL7CSB.
  --- Logical volume ---
      global/lvdisplay_shows_full_device_path not found in config: defaulting to 0
  LV Path                /dev/RHEL7CSB/VMs_lv
  LV Name                VMs_lv
  VG Name                RHEL7CSB
  LV UUID                iXOy1p-wczA-WEEy-mawN-EPOh-YZGy-KIpTls
  LV Write Access        read/write
  LV Creation host, time localhost.localdomain, 2015-04-15 15:52:53 +1000
  LV Status              available
  # open                 1
  LV Size                120.00 GiB
  Current LE             30720
  Segments               2
  Allocation             inherit
  Read ahead sectors     auto
  - currently set to     256
  Block device           253:4

      Processing LV NotBackedUp_lv in VG RHEL7CSB.
  --- Logical volume ---
      global/lvdisplay_shows_full_device_path not found in config: defaulting to 0
  LV Path                /dev/RHEL7CSB/NotBackedUp_lv
  LV Name                NotBackedUp_lv
  VG Name                RHEL7CSB
  LV UUID                8SI5e4-O5uA-TbNC-bZeY-1WPg-Zf3P-H63Xsi
  LV Write Access        read/write
  LV Creation host, time pwayper.remote.csb, 2015-04-15 16:30:00 +1000
  LV Status              available
  # open                 1
  LV Size                100.00 GiB
  Current LE             25600
  Segments               1
  Allocation             inherit
  Read ahead sectors     auto
  - currently set to     256
  Block device           253:5

      Processing LV ISOs_lv in VG RHEL7CSB.
  --- Logical volume ---
      global/lvdisplay_shows_full_device_path not found in config: defaulting to 0
  LV Path                /dev/RHEL7CSB/ISOs_lv
  LV Name                ISOs_lv
  VG Name                RHEL7CSB
  LV UUID                YVI2nw-7LOu-mseA-vQkC-HpcK-Xabx-WK23yM
  LV Write Access        read/write
  LV Creation host, time pwayper.remote.csb, 2015-04-15 16:30:52 +1000
  LV Status              available
  # open                 1
  LV Size                50.00 GiB
  Current LE             12800
  Segments               1
  Allocation             inherit
  Read ahead sectors     auto
  - currently set to     256
  Block device           253:6

      Processing LV RHEL6-pg-pgsql-lv in VG RHEL7CSB.
  --- Logical volume ---
      global/lvdisplay_shows_full_device_path not found in config: defaulting to 0
  LV Path                /dev/RHEL7CSB/RHEL6-pg-pgsql-lv
  LV Name                RHEL6-pg-pgsql-lv
  VG Name                RHEL7CSB
  LV UUID                USkJVW-ALIP-kcpt-Av5e-Vf2u-GqXr-1VXhb1
  LV Write Access        read/write
  LV Creation host, time pwayper.remote.csb, 2015-04-19 15:36:34 +1000
  LV Status              available
  # open                 0
  LV Size                40.00 GiB
  Current LE             10240
  Segments               1
  Allocation             inherit
  Read ahead sectors     auto
  - currently set to     256
  Block device           253:7

  --- Physical volumes ---
  PV Name               /dev/mapper/luks-96c66446-77fd-4431-9508-f6912bd84194
  PV UUID               EfWV9V-03CX-E6zc-JkMw-yQae-wdzp-Je1KUn
  PV Status             allocatable
  Total PE / Free PE    118466 / 4036

  PV Name               /dev/sde
  PV UUID               bh4MbE-USrx-6Xd0-3biH-8v5o-Ztzn-XvKUkX
  PV Status             allocatable
  Total PE / Free PE    715396 / 212932

      Unlocking /run/lock/lvm/V_RHEL7CSB
      Setting global/notify_dbus to 1
"""


class TestVGdisplay():
    def test_VgDisplay(self):
        vg_info = vgdisplay.VgDisplay(context_wrap(VGDISPLAY))
        assert hasattr(vg_info, 'vg_list')
        assert vg_info.vg_list[0].get('VG Name') == 'rhel_hp-dl160g8-3'
        assert vg_info.vg_list[0].get('Metadata Sequence No') == '5'
        assert vg_info.vg_list[1].get('VG UUID') == 'by0Dl3-0lpB-MxEz-f6GO-9LYO-YRAQ-GufNZN'
        assert hasattr(vg_info, 'debug_info')
        assert vg_info.debug_info[0] == "Couldn't find device with uuid VVLmw8-e2AA-ECfW-wDPl-Vnaa-0wW1-utv7tV."
        assert vg_info.debug_info[1] == "There are 1 physical volumes missing."

    def test_vgdisplay_vv(self):
        vg_info = vgdisplay.VgDisplay(context_wrap(VGDISPLAY_VV))

        # Volume group tests
        assert hasattr(vg_info, 'vg_list')
        vgdata = vg_info.vg_list
        assert isinstance(vgdata, list)
        assert len(vgdata) == 1
        vg = vgdata[0]
        assert isinstance(vg, dict)
        assert sorted(vg.keys()) == sorted([
            'VG Name', 'Format', 'Metadata Areas', 'Metadata Sequence No',
            'VG Access', 'VG Status', 'MAX LV', 'Cur LV', 'Open LV',
            'Max PV', 'Cur PV', 'Act PV', 'VG Size', 'PE Size', 'Total PE',
            'Alloc PE / Size', 'Free  PE / Size', 'VG UUID',
            'Logical Volumes', 'Physical Volumes'
        ])
        assert vg['VG Name'] == 'RHEL7CSB'
        assert vg['Format'] == 'lvm2'
        assert vg['Metadata Areas'] == '1'
        assert vg['Metadata Sequence No'] == '13'
        assert vg['VG Access'] == 'read/write'
        assert vg['VG Status'] == 'resizable'
        assert vg['MAX LV'] == '0'
        assert vg['Cur LV'] == '7'
        assert vg['Open LV'] == '6'
        assert vg['Max PV'] == '0'
        assert vg['Cur PV'] == '2'
        assert vg['Act PV'] == '1'
        assert vg['VG Size'] == '462.76 GiB'
        assert vg['PE Size'] == '4.00 MiB'
        assert vg['Total PE'] == '118466'
        assert vg['Alloc PE / Size'] == '114430 / 446.99 GiB'
        # Caveat Utilor: double space after Free for alignment purposes
        assert vg['Free  PE / Size'] == '4036 / 15.77 GiB'
        assert vg['VG UUID'] == 'aeMrAJ-QkAe-llvW-oAoE-CWLF-MnUd-edD1tI'

        # Logical volume tests
        assert isinstance(vg['Logical Volumes'], dict)
        assert len(vg['Logical Volumes']) == 7
        # Test the first LV and then get a few different keys
        assert sorted(vg['Logical Volumes'].keys()) == sorted([
            '/dev/RHEL7CSB/Home', '/dev/RHEL7CSB/ISOs_lv',
            '/dev/RHEL7CSB/NotBackedUp_lv', '/dev/RHEL7CSB/RHEL6-pg-pgsql-lv',
            '/dev/RHEL7CSB/Root', '/dev/RHEL7CSB/Swap', '/dev/RHEL7CSB/VMs_lv'
        ])
        lvhome = vg['Logical Volumes']['/dev/RHEL7CSB/Home']
        assert isinstance(lvhome, dict)
        assert sorted(lvhome.keys()) == sorted([
            'LV Path', 'LV Name', 'VG Name', 'LV UUID', 'LV Write Access',
            'LV Creation host, time', 'LV Status', '# open', 'LV Size',
            'Current LE', 'Segments', 'Allocation', 'Read ahead sectors',
            '- currently set to', 'Block device'
        ])
        assert lvhome['LV Path'] == '/dev/RHEL7CSB/Home'
        assert lvhome['LV Name'] == 'Home'
        assert lvhome['VG Name'] == 'RHEL7CSB'
        assert lvhome['LV UUID'] == 'IdRMoU-JorV-ChPg-F1zb-6np9-yc08-qxj08f'
        assert lvhome['LV Write Access'] == 'read/write'
        assert lvhome['LV Creation host, time'] == 'localhost, 2015-04-16 00:02:47 +1000'
        assert lvhome['LV Status'] == 'available'
        assert lvhome['# open'] == '1'
        assert lvhome['LV Size'] == '100.00 GiB'
        assert lvhome['Current LE'] == '25600'
        assert lvhome['Segments'] == '1'
        assert lvhome['Allocation'] == 'inherit'
        assert lvhome['Read ahead sectors'] == 'auto'
        assert lvhome['- currently set to'] == '256'
        assert lvhome['Block device'] == '253:3'

        # Physical volume tests
        assert isinstance(vg['Physical Volumes'], dict)
        assert len(vg['Physical Volumes']) == 2
        assert '/dev/mapper/luks-96c66446-77fd-4431-9508-f6912bd84194' in vg['Physical Volumes']
        pvluks = vg['Physical Volumes']['/dev/mapper/luks-96c66446-77fd-4431-9508-f6912bd84194']
        assert sorted(pvluks.keys()) == sorted([
            'PV Name', 'PV UUID', 'PV Status', 'Total PE / Free PE'
        ])
        assert pvluks['PV Name'] == '/dev/mapper/luks-96c66446-77fd-4431-9508-f6912bd84194'
        assert pvluks['PV UUID'] == 'EfWV9V-03CX-E6zc-JkMw-yQae-wdzp-Je1KUn'
        assert pvluks['PV Status'] == 'allocatable'
        assert pvluks['Total PE / Free PE'] == '118466 / 4036'

        # Debug info tests
        assert hasattr(vg_info, 'debug_info')
        assert isinstance(vg_info.debug_info, list)
        assert vg_info.debug_info == []
