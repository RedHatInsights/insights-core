""""
``test lsblk``
================
"""
from falafel.mappers import lsblk
from falafel.core.context import Context

LSBLK_DATA = ['NAME          MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT',
              'vda           252:0    0    9G  0 disk',
              '|-vda1        252:1    0  500M  0 part /boot',
              '`-vda2        252:2    0  8.5G  0 part',
              '  |-rhel-root 253:0    0  7.6G  0 lvm  /',
              '  |-rhel-swap 253:1    0  924M  0 lvm  [SWAP]',
              'sda             8:0    0  500G  0 disk',
              '|-sda1          8:1    0  500G  0 part /data']

# lsblk -P -o
LSBLK_EXT_DATA = """ALIGNMENT="0" DISC-ALN="0" DISC-GRAN="0B" DISC-MAX="0B" DISC-ZERO="0" FSTYPE="" GROUP="cdrom" KNAME="sr0" LABEL="" LOG-SEC="512" MAJ:MIN="11:0" MIN-IO="512" MODE="brw-rw----" MODEL="DVD+-RW DVD8801 " MOUNTPOINT="" NAME="sr0" OPT-IO="0" OWNER="root" PHY-SEC="512" RA="128" RM="1" RO="0" ROTA="1" RQ-SIZE="128" SCHED="cfq" SIZE="1024M" STATE="running" TYPE="rom" UUID=""
ALIGNMENT="0" DISC-ALN="0" DISC-GRAN="0B" DISC-MAX="0B" DISC-ZERO="0" FSTYPE="" GROUP="disk" KNAME="sda" LABEL="" LOG-SEC="512" MAJ:MIN="8:0" MIN-IO="512" MODE="brw-rw----" MODEL="WDC WD1600JS-75N" MOUNTPOINT="" NAME="sda" OPT-IO="0" OWNER="root" PHY-SEC="512" RA="128" RM="0" RO="0" ROTA="1" RQ-SIZE="128" SCHED="cfq" SIZE="149G" STATE="running" TYPE="disk" UUID=""
ALIGNMENT="0" DISC-ALN="0" DISC-GRAN="0B" DISC-MAX="0B" DISC-ZERO="0" FSTYPE="ext4" GROUP="disk" KNAME="sda1" LABEL="" LOG-SEC="512" MAJ:MIN="8:1" MIN-IO="512" MODE="brw-rw----" MODEL="" MOUNTPOINT="/boot" NAME="sda1" OPT-IO="0" OWNER="root" PHY-SEC="512" RA="128" RM="0" RO="0" ROTA="1" RQ-SIZE="128" SCHED="cfq" SIZE="500M" STATE="" TYPE="part" UUID="c7c4c016-8b00-4ded-bffb-5cc4719b7d45"
ALIGNMENT="0" DISC-ALN="0" DISC-GRAN="0B" DISC-MAX="0B" DISC-ZERO="0" FSTYPE="LVM2_member" GROUP="disk" KNAME="sda2" LABEL="" LOG-SEC="512" MAJ:MIN="8:2" MIN-IO="512" MODE="brw-rw----" MODEL="" MOUNTPOINT="" NAME="sda2" OPT-IO="0" OWNER="root" PHY-SEC="512" RA="128" RM="0" RO="0" ROTA="1" RQ-SIZE="128" SCHED="cfq" SIZE="148.5G" STATE="" TYPE="part" UUID="fFE3aA-ifqV-09uh-1u18-b3mV-73gK-FApXf1"
ALIGNMENT="0" DISC-ALN="0" DISC-GRAN="0B" DISC-MAX="0B" DISC-ZERO="0" FSTYPE="ext4" GROUP="disk" KNAME="dm-0" LABEL="" LOG-SEC="512" MAJ:MIN="253:0" MIN-IO="512" MODE="brw-rw----" MODEL="" MOUNTPOINT="/" NAME="vg_trex-lv_root" OPT-IO="0" OWNER="root" PHY-SEC="512" RA="128" RM="0" RO="0" ROTA="1" RQ-SIZE="128" SCHED="" SIZE="50G" STATE="running" TYPE="lvm" UUID="0618daba-8dc0-4a1c-926b-4a0f968da62e"
ALIGNMENT="0" DISC-ALN="0" DISC-GRAN="0B" DISC-MAX="0B" DISC-ZERO="0" FSTYPE="swap" GROUP="disk" KNAME="dm-1" LABEL="" LOG-SEC="512" MAJ:MIN="253:1" MIN-IO="512" MODE="brw-rw----" MODEL="" MOUNTPOINT="[SWAP]" NAME="vg_trex-lv_swap" OPT-IO="0" OWNER="root" PHY-SEC="512" RA="128" RM="0" RO="0" ROTA="1" RQ-SIZE="128" SCHED="" SIZE="3.4G" STATE="running" TYPE="lvm" UUID="102e1d8a-39c9-4065-ae16-d9cbd7162691"
ALIGNMENT="0" DISC-ALN="0" DISC-GRAN="0B" DISC-MAX="0B" DISC-ZERO="0" FSTYPE="ext4" GROUP="disk" KNAME="dm-2" LABEL="" LOG-SEC="512" MAJ:MIN="253:2" MIN-IO="512" MODE="brw-rw----" MODEL="" MOUNTPOINT="/home" NAME="vg_trex-lv_home" OPT-IO="0" OWNER="root" PHY-SEC="512" RA="128" RM="0" RO="0" ROTA="1" RQ-SIZE="128" SCHED="" SIZE="95.1G" STATE="running" TYPE="lvm" UUID="eee3252d-de08-4732-9d55-f2e33f878664" """


def test_lsblk():
    context = Context(content=LSBLK_DATA)
    results = lsblk.get_device_info(context)
    assert results is not None
    assert len(results) == 7
    rhel_root = None
    sda = None
    for result in results:
        if result['NAME'] == 'rhel-root':
            rhel_root = result
        elif result['NAME'] == 'sda':
            sda = result
    assert rhel_root is not None
    assert rhel_root['MAJ:MIN'] == "253:0"
    assert rhel_root['RM'] == "0"
    assert rhel_root['SIZE'] == "7.6G"
    assert rhel_root['RO'] == "0"
    assert rhel_root['TYPE'] == "lvm"
    assert rhel_root['MOUNTPOINT'] == "/"
    assert rhel_root.get('PARENT_NAME') == "vda2"
    assert sda is not None
    assert sda['MAJ:MIN'] == "8:0"
    assert sda['RM'] == "0"
    assert sda['SIZE'] == "500G"
    assert sda['RO'] == "0"
    assert sda['TYPE'] == "disk"
    assert 'MOUNTPOINT' not in sda
    assert 'PARENT_NAME' not in sda


def test_lsblk_ext():
    context = Context(content=LSBLK_EXT_DATA.splitlines())
    results = lsblk.get_device_extended_info(context)
    assert results is not None
    assert len(results) == 7
    sda1 = None
    for result in results:
        if result['NAME'] == 'sda1':
            sda1 = result
    assert sda1 is not None
    assert sda1['ALIGNMENT'] == "0"
    assert sda1['DISC-ALN'] == "0"
    assert sda1['DISC-GRAN'] == "0B"
    assert sda1['DISC-MAX'] == "0B"
    assert sda1['DISC-ZERO'] == "0"
    assert sda1['FSTYPE'] == "ext4"
    assert sda1['GROUP'] == "disk"
    assert sda1['KNAME'] == "sda1"
    assert 'LABEL' not in sda1
    assert sda1['LOG-SEC'] == "512"
    assert sda1['MAJ:MIN'] == "8:1"
    assert sda1['MIN-IO'] == "512"
    assert sda1['MODE'] == "brw-rw----"
    assert 'MODEL' not in sda1
    assert sda1['MOUNTPOINT'] == "/boot"
    assert sda1['NAME'] == "sda1"
    assert sda1['OPT-IO'] == "0"
    assert sda1['OWNER'] == "root"
    assert sda1['PHY-SEC'] == "512"
    assert sda1['RA'] == "128"
    assert sda1['RM'] == "0"
    assert sda1['RO'] == "0"
    assert sda1['ROTA'] == "1"
    assert sda1['RQ-SIZE'] == "128"
    assert sda1['SCHED'] == "cfq"
    assert sda1['SIZE'] == "500M"
    assert 'STATE' not in sda1
    assert sda1['TYPE'] == "part"
    assert sda1['UUID'] == "c7c4c016-8b00-4ded-bffb-5cc4719b7d45"
