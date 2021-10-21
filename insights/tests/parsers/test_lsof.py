import pytest
from insights.core.dr import SkipComponent
from insights.parsers import lsof
from insights.tests import context_wrap

LSOF = """
lsof: avoiding stat(/): -b was specified.
COMMAND     PID  TID           USER   FD      TYPE             DEVICE  SIZE/OFF       NODE NAME
systemd       1                root  cwd       DIR              253,1      4096        128 /
systemd       1                root  rtd       DIR              253,1      4096        128 /
systemd       1                root  txt       REG              253,1   1230920    1440410 /usr/lib/systemd/systemd
systemd       1                root  mem       REG              253,1     37152  135529970 /usr/lib64/libnss_sss.so.2
meventd     674  688           root  txt       REG              253,1     36344  135317954 /usr/sbin/dmeventd
dmeventd    674  688           root  mem       REG              253,1     20032  134413763 /usr/lib64/libuuid.so.1.3.0
dmeventd    674  688           root  mem       REG              253,1    248584  135108725 /usr/lib64/libblkid.so.1.1.0
bioset      611                root  txt   unknown                                         /proc/611/exe
systemd       1                root  cwd       DIR              253,1      4096        128 /
""".strip()

LSOF_GOOD_V1 = """
COMMAND    PID  TID           USER   FD      TYPE             DEVICE  SIZE/OFF       NODE NAME
systemd-l  602                root   14u      CHR              13,64       0t0       6406 /dev/input/event0
systemd-l  602                root   15u      CHR              13,65       0t0       6407 /dev/input/event1
systemd-l  602                root   16u      CHR                4,6       0t0       4694 /dev/tty6
dbus-daem  603                dbus    0r      CHR                1,3       0t0       4674 /dev/null
dbus-daem  603  615           dbus    0r      CHR                1,3       0t0       4674 /dev/null
abrt-watc 8619                root    0r      CHR                1,3       0t0       4674 /dev/null
wpa_suppl  641                root    0r      CHR                1,3       0t0       4674 /dev/null
polkitd    642             polkitd    0u      CHR                1,3       0t0       4674 /dev/null
polkitd    642             polkitd    1u      CHR                1,3       0t0       4674 /dev/null
polkitd    642             polkitd    2u      CHR                1,3       0t0       4674 /dev/null
gmain      642  643        polkitd    0u      CHR                1,3       0t0       4674 /dev/null
gmain      642  643        polkitd    1u      CHR                1,3       0t0       4674 /dev/null
gmain      642  643        polkitd    2u      CHR                1,3       0t0       4674 /dev/null
gdbus      642  646        polkitd    0u      CHR                1,3       0t0       4674 /dev/null
gdbus      642  646        polkitd    1u      CHR                1,3       0t0       4674 /dev/null
gdbus      642  646        polkitd    2u      CHR                1,3       0t0       4674 /dev/null
JS         642  648        polkitd    1r      BLK               8,16       0t0      16884 /dev/sda
JS         642  648        polkitd    1u      CHR                1,3       0t0       4674 /dev/null
JS         642  648        polkitd    2u      CHR                1,3       0t0       4674 /dev/null
""".strip()

LSOF_GOOD_V2 = """
lsof: avoiding readlink(/sys): -b was specified.
lsof: avoiding stat(/sys): -b was specified.
lsof: WARNING: can't stat() sysfs file system /sys
      Output information may be incomplete.
COMMAND       PID     USER   FD      TYPE             DEVICE  SIZE/OFF       NODE NAME
systemd         1        0  cwd       DIR              253,0       251        128 /
systemd         1        0    0u      CHR                1,3       0t0       1032 /dev/null
systemd         1        0   19u     unix 0xffff998f20251f80       0t0  132266239 /run/systemd/journal/stdout type=STREAM
blkcg_pun      36        0  txt   unknown                                         /proc/36/exe
rsyslogd   772018        0    5w      REG              253,6 151175680       1351 /var/log/messages-20210221 (deleted)
""".strip()

columns = ["COMMAND", "PID", "TID", "USER", "FD", "TYPE", "DEVICE", "SIZE/OFF", "NODE", "NAME"]


def test_lsof():
    ctx = context_wrap(LSOF)
    d = list(lsof.Lsof(ctx).parse(LSOF.splitlines()))

    assert set(columns) == set([k for f in d for k in f.keys()])
    assert d[0] == {
        "COMMAND": "systemd",
        "PID": "1",
        "TID": "",
        "USER": "root",
        "FD": "cwd",
        "TYPE": "DIR",
        "DEVICE": "253,1",
        "SIZE/OFF": "4096",
        "NODE": "128",
        "NAME": "/"
    }

    # Spot checks
    assert d[3]["TID"] == ""
    assert d[4]["TID"] == "688"
    assert d[5]["TYPE"] == "REG"
    assert d[7]["NAME"] == "/proc/611/exe"

    assert d[-2] == {
        "COMMAND": "bioset",
        "PID": "611",
        "TID": "",
        "USER": "root",
        "FD": "txt",
        "TYPE": "unknown",
        "DEVICE": "",
        "SIZE/OFF": "",
        "NODE": "",
        "NAME": "/proc/611/exe"
    }
    assert d[-1] == {
        "COMMAND": "systemd",
        "PID": "1",
        "TID": "",
        "USER": "root",
        "FD": "cwd",
        "TYPE": "DIR",
        "DEVICE": "253,1",
        "SIZE/OFF": "4096",
        "NODE": "128",
        "NAME": "/"
    }


def test_lsof_good():
    ctx = context_wrap(LSOF_GOOD_V1)
    d = list(lsof.Lsof(ctx).parse(LSOF_GOOD_V1.splitlines()))
    assert d[0] == {
        "COMMAND": "systemd-l",
        "PID": "602",
        "TID": "",
        "USER": "root",
        "FD": "14u",
        "TYPE": "CHR",
        "DEVICE": "13,64",
        "SIZE/OFF": "0t0",
        "NODE": "6406",
        "NAME": "/dev/input/event0"
    }

    # Spot checks
    assert d[3]["TID"] == ""
    assert d[4]["TID"] == "615"
    assert d[5]["COMMAND"] == "abrt-watc"
    assert d[5]["PID"] == "8619"
    assert d[5]["TYPE"] == "CHR"
    assert d[7]["NAME"] == "/dev/null"

    assert d[-1] == {
        "COMMAND": "JS",
        "PID": "642",
        "TID": "648",
        "USER": "polkitd",
        "FD": "2u",
        "TYPE": "CHR",
        "DEVICE": "1,3",
        "SIZE/OFF": "0t0",
        "NODE": "4674",
        "NAME": "/dev/null"
    }


def test_lsof_good_v2():
    ctx = context_wrap(LSOF_GOOD_V2)
    d = list(lsof.Lsof(ctx).parse(LSOF_GOOD_V2.splitlines()))
    assert d[0] == {
        'COMMAND': 'systemd',
        'PID': '1',
        'USER': '0',
        'FD': 'cwd',
        'TYPE': 'DIR',
        'DEVICE': '253,0',
        'SIZE/OFF': '251',
        'NODE': '128',
        'NAME': '/'
    }

    # wide and empty values checks
    assert d[2]['DEVICE'] == '0xffff998f20251f80'
    assert d[3]['DEVICE'] == ''

    assert d[-1] == {
        'COMMAND': 'rsyslogd',
        'PID': '772018',
        'USER': '0',
        'FD': '5w',
        'TYPE': 'REG',
        'DEVICE': '253,6',
        'SIZE/OFF': '151175680',
        'NODE': '1351',
        'NAME': '/var/log/messages-20210221 (deleted)'
    }


def test_lsof_scan():
    ctx = context_wrap(LSOF_GOOD_V1)
    # Scannable provided `any` method
    lsof.Lsof.any('systemd_commands', lambda x: 'systemd' in x['COMMAND'])
    # Scannable provided `collect` method
    lsof.Lsof.collect('polkitd_user', lambda x: x['USER'] == 'polkitd')
    # Lsof provided `collect_keys` method
    lsof.Lsof.collect_keys('root_stdin', USER='root', FD='0r', SIZE_OFF='0t0')
    l = lsof.Lsof(ctx)
    assert l.systemd_commands
    assert len(l.polkitd_user) == 12

    assert hasattr(l, 'root_stdin')
    assert len(l.root_stdin) == 2

    assert l.root_stdin[0]['COMMAND'] == 'abrt-watc'
    assert l.root_stdin[0]['PID'] == '8619'
    assert l.root_stdin[0]['TID'] == ''
    assert l.root_stdin[0]['USER'] == 'root'
    assert l.root_stdin[0]['FD'] == '0r'
    assert l.root_stdin[0]['TYPE'] == 'CHR'
    assert l.root_stdin[0]['DEVICE'] == '1,3'
    assert l.root_stdin[0]['SIZE/OFF'] == '0t0'
    assert l.root_stdin[0]['NODE'] == '4674'
    assert l.root_stdin[0]['NAME'] == '/dev/null'

    assert l.root_stdin[1]['COMMAND'] == 'wpa_suppl'
    assert l.root_stdin[1]['PID'] == '641'
    assert l.root_stdin[1]['TID'] == ''
    assert l.root_stdin[1]['USER'] == 'root'
    assert l.root_stdin[1]['FD'] == '0r'
    assert l.root_stdin[1]['TYPE'] == 'CHR'
    assert l.root_stdin[1]['DEVICE'] == '1,3'
    assert l.root_stdin[1]['SIZE/OFF'] == '0t0'
    assert l.root_stdin[1]['NODE'] == '4674'
    assert l.root_stdin[1]['NAME'] == '/dev/null'


LSOF_BAD = """
lsof: WARNING: can't stat() xfs file system /var/lib/origin/openshift.local.volumes/pods/abca2a21-da4c-22eb-b49c-011d3a938eb5/volume-subpaths/config/wh/0
"""


def test_lsof_bad():
    with pytest.raises(SkipComponent) as e:
        lsof.Lsof(context_wrap(LSOF_BAD))
    assert e is not None
