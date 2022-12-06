import doctest

from insights.parsers import ls_bin
from insights.tests import context_wrap


LS_BIN = """
total 214536
dr-xr-xr-x.  2 0  0    49152 Nov  4 04:58 .
drwxr-xr-x. 12 0  0      144 May 29  2022 ..
-rwxr-xr-x.  1 0  0    54008 May 31  2022 [
-rwxr-xr-x.  1 0  0    33416 Nov  1  2021 ac
-rwxr-xr-x.  1 0  0    24480 Jul  9 05:16 aconnect
-rwxr-xr-x.  1 0  0    29080 Jun 14 10:04 addr2line
-rwxr-xr-x.  1 0  0   154416 Aug 10  2021 airscan-discover
-rwxr-xr-x.  1 0  0    28584 Jul  9 05:16 aplaymidi
-rwxr-xr-x.  1 0  0   127680 Sep 30  2021 appstreamcli
-rwxr-xr-x.  1 0  0    32616 Aug  9  2021 appstream-compose
-rwxr-xr-x.  1 0  0   119848 Aug  9  2021 appstream-util
lrwxrwxrwx.  1 0  0       25 May 29  2022 apropos -> /etc/alternatives/apropos
lrwxrwxrwx.  1 0  0        6 Aug 10  2021 apropos.man-db -> whatis
lrwxrwxrwx.  1 0  0        5 Aug  9  2021 bunzip2 -> bzip2
-rwxr-xr-x.  1 0  0   102512 Aug 25 05:11 busctl
-rwxr-xr-x.  1 0  0    74536 Aug  9  2021 bwrap
lrwxrwxrwx.  1 0  0        5 Aug  9  2021 bzcat -> bzip2
lrwxrwxrwx.  1 0  0        6 Aug  9  2021 bzcmp -> bzdiff
-rwxr-xr-x.  1 0  0     2144 Aug  9  2021 bzdiff
lrwxrwxrwx.  1 0  0        6 Aug  9  2021 bzegrep -> bzgrep
lrwxrwxrwx.  1 0  0        6 Aug  9  2021 bzfgrep -> bzgrep
-rwxr-xr-x.  1 0  0     2058 Aug  9  2021 bzgrep
-rwxr-xr-x.  1 0  0    41048 Aug  9  2021 bzip2
-rwxr-xr-x.  1 0  0    16256 Aug  9  2021 bzip2recover
lrwxrwxrwx.  1 0  0        6 Aug  9  2021 bzless -> bzmore
-rwxr-xr-x.  1 0  0     1263 Aug  9  2021 bzmore
-rwxr-xr-x.  1 0  0    53072 Aug 24 11:22 cal
-rwxr-xr-x.  1 0  0     1648 Jul 28 15:03 ca-legacy
-rwxr-xr-x.  1 0  0    28744 Aug 10  2021 calibrate_ppa
-rwxr-xr-x.  1 0  0    20104 Aug  9  2021 canberra-boot
-rwxr-xr-x.  1 0  0    20224 Aug  9  2021 canberra-gtk-play
lrwxrwxrwx.  1 0  0       30 May 29  2022 cancel -> /etc/alternatives/print-cancel
-rwxr-xr-x.  1 0  0    16088 Jun 16 09:19 cancel.cups
lrwxrwxrwx.  1 0  0        3 Aug 10  2021 captoinfo -> tic
-rwxr-xr-x.  1 0  0    37464 May 31  2022 cat
-rwxr-xr-x.  1 0  0     3289 Jul 24 06:34 catchsegv
"""

LS_BIN_EXAMPLE = """
total 214536
dr-xr-xr-x.  2 0  0    49152 Nov  4 04:58 .
drwxr-xr-x. 12 0  0      144 May 29  2022 ..
-rwxr-xr-x.  1 0  0    54008 May 31  2022 [
-rwxr-xr-x.  1 0  0    33416 Nov  1  2021 ac
-rwxr-xr-x.  1 0  0    24480 Jul  9 05:16 aconnect
-rwxr-xr-x.  1 0  0    29080 Jun 14 10:04 addr2line
lrwxrwxrwx.  1 0  0       25 May 29  2022 apropos -> /etc/alternatives/apropos
lrwxrwxrwx.  1 0  0        6 Aug 10  2021 apropos.man-db -> whatis
-rwxr-xr-x.  1 0  0    58000 Jun 14 10:04 ar
-rwxr-xr-x.  1 0  0    33368 May 31  2022 arch
lrwxrwxrwx.  1 0  0        5 Jul  9 05:16 arecord -> aplay
"""


def test_ls_etc_ssh():
    ls_bin_res = ls_bin.LsBin(context_wrap(LS_BIN, path='ls_-lan_.bin'))
    assert '/bin' in ls_bin_res
    assert len(ls_bin_res.files_of("/bin")) == 34
    assert 'bzgrep' in ls_bin_res.files_of("/bin")
    assert ls_bin_res.dirs_of("/bin") == ['.', '..']
    assert ls_bin_res.listing_of("/bin")['captoinfo'] == {'group': '0', 'name': 'captoinfo', 'link': 'tic', 'links': 1, 'perms': 'rwxrwxrwx.', 'raw_entry': 'lrwxrwxrwx.  1 0  0        3 Aug 10  2021 captoinfo -> tic', 'owner': '0', 'date': 'Aug 10  2021', 'type': 'l', 'dir': '/bin', 'size': 3}


def test_ls_etc_documentation():
    failed_count, tests = doctest.testmod(
        ls_bin,
        globs={'ls_bin': ls_bin.LsBin(context_wrap(LS_BIN_EXAMPLE, path='ls_-lan_.bin'))}
    )
    assert failed_count == 0
