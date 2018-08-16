import doctest

from insights.parsers import ls_lib_firmware
from insights.parsers.ls_lib_firmware import LsLibFW
from insights.tests import context_wrap

LS_LIB_FW = """
/lib/firmware:
total 37592
drwxr-xr-x. 83 0 0    8192 Aug 14 02:43 .
dr-xr-xr-x. 26 0 0    4096 Aug 14 02:22 ..
drwxr-xr-x.  2 0 0      40 Aug 14 02:42 3com
lrwxrwxrwx.  1 0 0      16 Aug 14 02:42 a300_pfp.fw -> qcom/a300_pfp.fw
lrwxrwxrwx.  1 0 0      16 Aug 14 02:42 a300_pm4.fw -> qcom/a300_pm4.fw
drwxr-xr-x.  2 0 0      34 Aug 14 02:42 acenic
drwxr-xr-x.  2 0 0      50 Aug 14 02:42 adaptec
drwxr-xr-x.  2 0 0      73 Aug 14 02:42 advansys

/lib/firmware/3com:
total 84
drwxr-xr-x.  2 0 0    40 Aug 14 02:42 .
drwxr-xr-x. 83 0 0  8192 Aug 14 02:43 ..
-rw-r--r--.  1 0 0 24880 Jun  6 10:14 3C359.bin
-rw-r--r--.  1 0 0 44548 Jun  6 10:14 typhoon.bin

/lib/firmware/acenic:
total 160
drwxr-xr-x.  2 0 0    34 Aug 14 02:42 .
drwxr-xr-x. 83 0 0  8192 Aug 14 02:43 ..
-rw-r--r--.  1 0 0 73116 Jun  6 10:14 tg1.bin
-rw-r--r--.  1 0 0 77452 Jun  6 10:14 tg2.bin

/lib/firmware/adaptec:
total 20
drwxr-xr-x.  2 0 0   50 Aug 14 02:42 .
drwxr-xr-x. 83 0 0 8192 Aug 14 02:43 ..
-rw-r--r--.  1 0 0  832 Jun  6 10:14 starfire_rx.bin
-rw-r--r--.  1 0 0  832 Jun  6 10:14 starfire_tx.bin

/lib/firmware/advansys:
total 40
drwxr-xr-x.  2 0 0   73 Aug 14 02:42 .
drwxr-xr-x. 83 0 0 8192 Aug 14 02:43 ..
-rw-r--r--.  1 0 0 5026 Jun  6 10:14 3550.bin
-rw-r--r--.  1 0 0 5340 Jun  6 10:14 38C0800.bin
-rw-r--r--.  1 0 0 6334 Jun  6 10:14 38C1600.bin
-rw-r--r--.  1 0 0 2308 Jun  6 10:14 mcode.bin

/lib/firmware/bnx2:
total 1448
drwxr-xr-x.  2 0 0   4096 Aug 14 02:43 .
drwxr-xr-x. 83 0 0   8192 Aug 14 02:43 ..
-rw-r--r--.  1 0 0  92628 Jun  6 10:14 bnx2-mips-06-4.6.16.fw
-rw-r--r--.  1 0 0  93172 Jun  6 10:14 bnx2-mips-06-5.0.0.j3.fw
-rw-r--r--.  1 0 0  94252 Jun  6 10:14 bnx2-mips-06-5.0.0.j6.fw
-rw-r--r--.  1 0 0  92824 Jun  6 10:14 bnx2-mips-06-6.2.3.fw
-rw-r--r--.  1 0 0  92760 Jun  6 10:14 bnx2-mips-09-4.6.17.fw
-rw-r--r--.  1 0 0  96996 Jun  6 10:14 bnx2-mips-09-5.0.0.j15.fw

/lib/firmware/bnx2x:
total 8772
drwxr-xr-x.  2 0 0   4096 Aug 14 02:43 .
drwxr-xr-x. 83 0 0   8192 Aug 14 02:43 ..
-rw-r--r--.  1 0 0 151568 Jun  6 10:14 bnx2x-e1-6.0.34.0.fw
-rw-r--r--.  1 0 0 151680 Jun  6 10:14 bnx2x-e1-6.2.5.0.fw
-rw-r--r--.  1 0 0 151688 Jun  6 10:14 bnx2x-e1-6.2.9.0.fw
-rw-r--r--.  1 0 0 161144 Jun  6 10:14 bnx2x-e1-7.0.20.0.fw
-rw-r--r--.  1 0 0 161248 Jun  6 10:14 bnx2x-e1-7.0.23.0.fw
""".strip()


def test_ls_lib_firmware():
    lslib = LsLibFW(context_wrap(LS_LIB_FW))
    assert "bnx2x" not in lslib
    assert "/lib/firmware/bnx2" in lslib
    assert "/lib/firmware/bnx2x" in lslib
    assert lslib.dirs_of("/lib/firmware") == ['.', '..', '3com', 'acenic', 'adaptec', 'advansys']
    assert lslib.files_of("/lib/firmware/bnx2x") == ['bnx2x-e1-6.0.34.0.fw', 'bnx2x-e1-6.2.5.0.fw', 'bnx2x-e1-6.2.9.0.fw', 'bnx2x-e1-7.0.20.0.fw', 'bnx2x-e1-7.0.23.0.fw']
    assert "bnx2x-e1-6.0.34.0.fw" in lslib.files_of("/lib/firmware/bnx2x")
    assert lslib.dir_contains("/lib/firmware/bnx2x", "bnx2x-e1-6.0.34.0.fw") is True
    assert lslib.total_of("/lib/firmware") == 37592


def test_ls_lib_firmware_doc_examples():
    env = {
        'lslibfw': LsLibFW(context_wrap(LS_LIB_FW)),
    }
    failed, total = doctest.testmod(ls_lib_firmware, globs=env)
    assert failed == 0
