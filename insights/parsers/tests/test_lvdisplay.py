#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from insights.tests import context_wrap
from insights.parsers.lvdisplay import LvDisplay

LV_DISPLAY = """
      Adding lvsapp01ap01:0 as an user of lvsapp01ap01_mlog
  --- Volume group ---
  VG Name               vgp01app
  Format                lvm2
  Metadata Areas        4
  Metadata Sequence No  56
  VG Access             read/write
  VG Status             resizable
  Clustered             yes
  Shared                no
  MAX LV                0
  Cur LV                4
  Open LV               1
  Max PV                0
  Cur PV                4
  Act PV                4
  VG Size               399.98 GiB
  PE Size               4.00 MiB
  Total PE              102396
  Alloc PE / Size       82435 / 322.01 GiB
  Free  PE / Size       19961 / 77.97 GiB
  VG UUID               JVgCxE-UY84-C0Gk-8Cmn-UGXu-UHo0-9Qa4Re

  --- Logical volume ---
      global/lvdisplay_shows_full_device_path not found in config: defaulting to 0
  LV Path                /dev/vgp01app/lvsapp01ap01-old
  LV Name                lvsapp01ap01-old
  VG Name                vgp01app
  LV UUID                eLjsoG-Gvnh-zEbV-zFwD-HyQT-1zEs-VN4W2D
  LV Write Access        read/write
  LV Creation host, time lvn-itm-099, 2015-02-24 09:19:54 +0100
  LV Status              available
  # open                 0
  LV Size                64.00 GiB
  Current LE             16384
  Segments               4
  Allocation             inherit
  Read ahead sectors     auto
  - currently set to     256
  Block device           253:50

  --- Logical volume ---
      global/lvdisplay_shows_full_device_path not found in config: defaulting to 0
  LV Path                /dev/vgp01app/lvsapp01ap02
  LV Name                lvsapp01ap02
  VG Name                vgp01app
  LV UUID                tFGsSW-nimQ-4JUL-4Fw0-IJn0-Jcoo-Szgfgz
  LV Write Access        read/write
  LV Creation host, time lvn-itm-099, 2015-02-24 15:24:52 +0100
  LV Status              available
  # open                 0
  LV Size                64.00 GiB
  Current LE             16384
  Mirrored volumes       2
  Segments               1
  Allocation             inherit
  Read ahead sectors     auto
  - currently set to     256
  Block device           253:54
"""


def test_lvdisplay():
    lvs = LvDisplay(context_wrap(LV_DISPLAY))
    assert 'vgp01app' == lvs.get('volumes')['Volume group'][0]['VG Name']
    assert '399.98 GiB' == lvs.get('volumes')['Volume group'][0]['VG Size']
    assert 'vgp01app' == lvs.get('volumes')['Logical volume'][1]['VG Name']
    assert 'vgp01app' in lvs.vgs
    assert lvs.vgs['vgp01app'] == lvs.get('volumes')['Volume group'][0]
    assert 'lvsapp01ap02' in lvs.lvs
    assert lvs.lvs['lvsapp01ap02'] == lvs.get('volumes')['Logical volume'][1]
