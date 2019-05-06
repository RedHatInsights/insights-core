# -*- coding: UTF-8 -*-
import six
from insights.core.ls_parser import parse


SINGLE_DIRECTORY = """
total 32
drwxr-xr-x.  5 root root  4096 Jun 28  2017 .
drwxr-xr-x. 15 root root  4096 Aug 10 09:42 ..
lrwxrwxrwx.  1 root root    49 Jun 28  2017 cert.pem -> /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem
drwxr-xr-x.  2 root root  4096 Jun 28  2017 certs
drwxr-xr-x.  2 root root  4096 Mar 29  2017 misc
-rw-r--r--.  1 root root 10923 Feb  7  2017 openssl.cnf
drwxr-xr-x.  2 root root  4096 Feb  7  2017 private
"""

MULTIPLE_DIRECTORIES = """
/etc/sysconfig:
total 96
drwxr-xr-x.  7 0 0 4096 Jul  6 23:41 .
drwxr-xr-x. 77 0 0 8192 Jul 13 03:55 ..
drwxr-xr-x.  2 0 0   41 Jul  6 23:32 cbq
drwxr-xr-x.  2 0 0    6 Sep 16  2015 console
-rw-------.  1 0 0 1390 Mar  4  2014 ebtables-config
-rw-r--r--.  1 0 0   72 Sep 15  2015 firewalld
lrwxrwxrwx.  1 0 0   17 Jul  6 23:32 grub -> /etc/default/grub

/etc/rc.d/rc3.d:
total 4
drwxr-xr-x.  2 0 0   58 Jul  6 23:32 .
drwxr-xr-x. 10 0 0 4096 Sep 16  2015 ..
lrwxrwxrwx.  1 0 0   20 Jul  6 23:32 K50netconsole -> ../init.d/netconsole
lrwxrwxrwx.  1 0 0   17 Jul  6 23:32 S10network -> ../init.d/network
lrwxrwxrwx.  1 0 0   15 Jul  6 23:32 S97rhnsd -> ../init.d/rhnsd
"""

MULTIPLE_DIRECTORIES_WITH_BREAK = """
/etc:
total 1652
drwxr-xr-x. 102   0   0  12288 Nov  6 09:12 .
dr-xr-xr-x.  21   0   0   4096 Oct 23 10:12 ..
-rw-------.   1   0   0      0 Oct  2 13:46 .pwd.lock
-rw-r--r--    1   0   0    163 Oct  2 13:45 .updated
-rw-r--r--.   1   0   0   1059 Oct  2 13:56 chrony.conf
-rw-r--r--.   1   0   0   1100 Dec  5  2017 chrony.conf.20180210135613

-rw-r-----.   1   0 993    481 Sep 14  2017 chrony.keys
drwxr-xr-x.   2   0   0   4096 Nov  1 03:34 cifs-utils

/etc/sysconfig:
total 96
drwxr-xr-x.  7 0 0 4096 Jul  6 23:41 .
drwxr-xr-x. 77 0 0 8192 Jul 13 03:55 ..
drwxr-xr-x.  2 0 0   41 Jul  6 23:32 cbq
drwxr-xr-x.  2 0 0    6 Sep 16  2015 console
-rw-------.  1 0 0 1390 Mar  4  2014 ebtables-config
-rw-r--r--.  1 0 0   72 Sep 15  2015 firewalld
lrwxrwxrwx.  1 0 0   17 Jul  6 23:32 grub -> /etc/default/grub

/etc/rc.d/rc3.d:
total 4
drwxr-xr-x.  2 0 0   58 Jul  6 23:32 .
drwxr-xr-x. 10 0 0 4096 Sep 16  2015 ..
lrwxrwxrwx.  1 0 0   20 Jul  6 23:32 K50netconsole -> ../init.d/netconsole
lrwxrwxrwx.  1 0 0   17 Jul  6 23:32 S10network -> ../init.d/network
lrwxrwxrwx.  1 0 0   15 Jul  6 23:32 S97rhnsd -> ../init.d/rhnsd
"""


COMPLICATED_FILES = """
/tmp:
total 16
dr-xr-xr-x.  2 0 0     4096 Mar  4 16:19 .
dr-xr-xr-x. 10 0 0     4096 Mar  4 16:19 ..
-rw-r--r--.  1 0 0   123891 Aug 25  2015 config-3.10.0-229.14.1.el7.x86_64
lrwxrwxrwx.  1 0 0       11 Aug  4  2014 menu.lst -> ./grub.conf
brw-rw----.  1 0 6 253,  10 Aug  4 16:56 dm-10
crw-------.  1 0 0 10,  236 Jul 25 10:00 control
srw-------.  1 26214 17738 0 Oct 19 08:48 geany_socket.c46453c2
-rw-rw-r--.  1 24306 24306 13895 Oct 21 15:42 File name with spaces in it!
-rw-rw-r--.  1 24306 24306 13895 Oct 21 15:42 Unicode ÅÍÎÏÓÔÒÚÆ☃ madness.txt
drwxr-xr-x+  2 0 0       41 Jul  6 23:32 additional_ACLs
brw-rw----.  1 0 6  1048576 Aug  4 16:56 block dev with no comma also valid
-rwxr-xr-x.  2 0 0     1024 Jul  6 23:32 file_name_ending_with_colon:
lrwxrwxrwx.  1 0 0       11 Aug  4  2014 link with spaces -> ../file with spaces
"""

COMPLICATED_FILES_BAD_LINE = """
/tmp:
total 16
dr-xr-xr-x.  2 0 0     4096 Mar  4 16:19 .
dr-xr-xr-x. 10 0 0     4096 Mar  4 16:19 ..
-rw-r--r--.  1 0 0   123891 Aug 25  2015 config-3.10.0-229.14.1.el7.x86_64
ls: cannot open directory '/etc/audisp': Permission denied
lrwxrwxrwx.  1 0 0       11 Aug  4  2014 menu.lst -> ./grub.conf
brw-rw----.  1 0 6 253,  10 Aug  4 16:56 dm-10
crw-------.  1 0 0 10,  236 Jul 25 10:00 control
srw-------.  1 26214 17738 0 Oct 19 08:48 geany_socket.c46453c2
-rw-rw-r--.  1 24306 24306 13895 Oct 21 15:42 File name with spaces in it!
-rw-rw-r--.  1 24306 24306 13895 Oct 21 15:42 Unicode ÅÍÎÏÓÔÒÚÆ☃ madness.txt
drwxr-xr-x+  2 0 0       41 Jul  6 23:32 additional_ACLs
brw-rw----.  1 0 6  1048576 Aug  4 16:56 block dev with no comma also valid
-rwxr-xr-x.  2 0 0     1024 Jul  6 23:32 file_name_ending_with_colon:
lrwxrwxrwx.  1 0 0       11 Aug  4  2014 link with spaces -> ../file with spaces
"""

SELINUX_DIRECTORY = """
/boot:
total 3
-rw-r--r--. root root system_u:object_r:boot_t:s0      config-3.10.0-267
drwxr-xr-x. root root system_u:object_r:boot_t:s0      grub2
-rw-r--r--. root root system_u:object_r:boot_t:s0      initramfs-0-rescue
"""

RHEL8_SELINUX_DIRECTORY = """
/var/lib/nova/instances:
total 0
drwxr-xr-x. 3 root root unconfined_u:object_r:var_lib_t:s0 50 Apr  8 16:41 .
drwxr-xr-x. 3 root root unconfined_u:object_r:var_lib_t:s0 23 Apr  8 16:29 ..
drwxr-xr-x. 2 root root unconfined_u:object_r:var_lib_t:s0 54 Apr  8 16:41 abcd-efgh-ijkl-mnop
"""

FILES_CREATED_WITH_SELINUX_DISABLED = """
/dev/mapper:
total 2
lrwxrwxrwx 1 0 0 7 Apr 27 05:34 lv_cpwtk001_data01 -> ../dm-7
lrwxrwxrwx 1 0 0 7 Apr 27 05:34 lv_cpwtk001_redo01 -> ../dm-8
"""

BAD_DIRECTORY_ENTRIES = """
dr-xr-xr-x.  2 0 0     4096 Mar  4 16:19 dir entry with no dir header
total 3

/badness:
    -rwxr-xr-x. 0 0    1 Sep 12 2010 indented entry
xr-xr--r--. 0 0        1 Sep 12  2010 bad file type
-rxr-xr-x.  0 0        1 Sep 12  2010 missing user w permission
-rwxr-xr-x  0 0        1 Sep 12  2010 missing ACL dot
-rw-r--r--. user with spaces group 2 Oct 3 2011 user with spaces
-rw-r--r--. user group with spaces 2 Oct 3 2011 group with spaces
dr-xr-xr-x. -42 -63 1271 Jan  6  2008 Negative user and group numbers
dr-xr-xr-x. 1 7 123, 124, 125 Jan 6 2008 Three comma blocks in size
brw-rw----. 1 0 6 123456 Aug 4 16:56 two size blocks
prw-rw----. 1000 1000  0  6 2007 Month missing
prw-rw----. 1000 1000  0 No 6 2007 Month too short
prw-rw----. 1000 1000  0 November 6 2007 Month too long
prw-rw----. 1000 1000  0 Nov  2007 Day too long
prw-rw----. 1000 1000  0 Nov 126 2007 Day too long
prw-rw----. 1000 1000  0 Nov 126  Year missing
prw-rw----. 1000 1000  0 Nov 126 20107 Year too long
prw-rw----. 1000 1000  0 Nov 12 :56 Missing hour
prw-rw----. 1000 1000  0 Nov 12 723:56 Hour too long
prw-rw----. 1000 1000  0 Nov 12 23: Missing minute
prw-rw----. 1000 1000  0 Nov 12 23:3 Minute too short
prw-rw----. 1000 1000  0 Nov 12 23:357 Minute too long
-rw------ 1 root root 762 Sep 23 002 permission too short
bash: ls: command not found
-rw------ 1 root root 762 Se
-rw------- 1 ro:t root 762 Sep 23 002 colon in uid
-rw------- 1 root r:ot 762 Sep 23 002 colon in gid
-rwasdfas- 1 root root 762 Sep 23 002 bad permissions block
-rwx/----- 1 root root 762 Sep 23 002 slash in permissions block
-rwx------ 1 root root 762 Sep 23 002 /slashes/in/filename
/rwasdfas- 1 root root 762 Sep 23 002 slash in file type and no colon on end
/usr/bin/ls: cannot access /boot/grub2/grub.cfg: No such file or directory
cannot access /boot/grub2/grub.cfg: No such file or directory
No such file or directory
adsf
"""


def test_parse_selinux():
    results = parse(SELINUX_DIRECTORY.splitlines(), "/boot")
    stanza = results["/boot"]
    assert stanza["name"] == "/boot"
    assert stanza["total"] == 3
    assert len(stanza["entries"]) == 3
    res = stanza["entries"]["config-3.10.0-267"]
    assert res["type"] == "-"
    assert res["owner"] == "root"
    assert res["group"] == "root"
    assert res["se_user"] == "system_u"
    assert res["se_role"] == "object_r"
    assert res["se_type"] == "boot_t"
    assert res["se_mls"] == "s0"
    assert res["name"] == "config-3.10.0-267"


def test_parse_single_directory():
    results = parse(SINGLE_DIRECTORY.splitlines(), "/etc")
    stanza = results["/etc"]
    assert stanza["name"] == "/etc"
    assert stanza["total"] == 32
    assert len(stanza["entries"]) == 7
    res = stanza["entries"]["cert.pem"]
    assert res["type"] == "l"
    assert res["owner"] == "root"
    assert res["group"] == "root"
    assert res["date"] == "Jun 28  2017"
    assert res["name"] == "cert.pem"
    assert res["link"] == "/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem"
    assert res["links"] == 1
    assert res["dir"] == "/etc"


def test_parse_multiple_directories():
    results = parse(MULTIPLE_DIRECTORIES.splitlines(), None)
    assert len(results) == 2, len(results)
    assert results["/etc/sysconfig"]["name"] == "/etc/sysconfig"
    assert results["/etc/sysconfig"]["total"] == 96
    assert results["/etc/rc.d/rc3.d"]["name"] == "/etc/rc.d/rc3.d"
    assert results["/etc/rc.d/rc3.d"]["total"] == 4

    res = results["/etc/sysconfig"]["entries"]["ebtables-config"]
    assert res["type"] == "-"
    assert res["links"] == 1
    assert res["owner"] == "0"
    assert res["group"] == "0"
    assert res["size"] == 1390
    assert res["date"] == "Mar  4  2014"
    assert res["name"] == "ebtables-config"
    assert res["dir"] == "/etc/sysconfig"


def test_parse_multiple_directories_with_break():
    results = parse(MULTIPLE_DIRECTORIES_WITH_BREAK.splitlines(), None)
    assert len(results) == 3, len(results)
    assert len(results.values()) == 3
    assert len(results.items()) == 3
    assert len(list(six.iteritems(results))) == 3
    assert results["/etc"]["name"] == "/etc"
    assert results["/etc"]["total"] == 1652
    assert results["/etc/rc.d/rc3.d"]["name"] == "/etc/rc.d/rc3.d"
    assert results["/etc/rc.d/rc3.d"]["total"] == 4

    res = results["/etc"]["entries"]["chrony.conf.20180210135613"]
    assert res["type"] == "-"
    assert res["links"] == 1
    assert res["owner"] == "0"
    assert res["group"] == "0"
    assert res["size"] == 1100
    assert res["date"] == "Dec  5  2017"
    assert res["name"] == "chrony.conf.20180210135613"
    assert res["dir"] == "/etc"


def test_complicated_files():
    results = parse(COMPLICATED_FILES.splitlines(), "/tmp")
    assert len(results) == 1
    assert results["/tmp"]["total"] == 16, results["/tmp"]["total"]
    assert results["/tmp"]["name"] == "/tmp", results["/tmp"]["name"]
    res = results["/tmp"]["entries"]["dm-10"]
    assert res["type"] == "b"
    assert res["links"] == 1
    assert res["owner"] == "0"
    assert res["group"] == "6"
    assert res["major"] == 253
    assert res["minor"] == 10
    assert res["date"] == "Aug  4 16:56"
    assert res["name"] == "dm-10"
    assert res["dir"] == "/tmp"


def test_files_with_selinux_disabled():
    results = parse(FILES_CREATED_WITH_SELINUX_DISABLED.splitlines(), "/dev/mapper")
    assert len(results) == 1
    assert results["/dev/mapper"]["total"] == 2
    assert results["/dev/mapper"]["name"] == "/dev/mapper", results[0]["name"]
    res = results["/dev/mapper"]["entries"]["lv_cpwtk001_data01"]
    assert res["type"] == "l"
    assert res["links"] == 1
    assert res["owner"] == "0"
    assert res["group"] == "0"
    assert res["size"] == 7
    assert res["date"] == "Apr 27 05:34"
    assert res["name"] == "lv_cpwtk001_data01"
    assert res["link"] == "../dm-7"
    assert res["dir"] == "/dev/mapper"


def test_bad_line():
    results = parse(COMPLICATED_FILES_BAD_LINE.splitlines(), "/tmp")
    assert len(results) == 1
    assert results["/tmp"]["total"] == 16, results["/tmp"]["total"]
    assert results["/tmp"]["name"] == "/tmp", results["/tmp"]["name"]
    res = results["/tmp"]["entries"]["dm-10"]
    assert res["type"] == "b"
    assert res["links"] == 1
    assert res["owner"] == "0"
    assert res["group"] == "6"
    assert res["major"] == 253
    assert res["minor"] == 10
    assert res["date"] == "Aug  4 16:56"
    assert res["name"] == "dm-10"
    assert res["dir"] == "/tmp"


def test_rhel8_selinux():
    results = parse(RHEL8_SELINUX_DIRECTORY.splitlines(), "/var/lib/nova/instances")
    assert len(results) == 1
    assert results["/var/lib/nova/instances"]["name"] == "/var/lib/nova/instances", results["/var/lib/nova/instances"]["name"]
    res = results["/var/lib/nova/instances"]["entries"]["abcd-efgh-ijkl-mnop"]
    assert results["/var/lib/nova/instances"]["total"] == 0, results["/var/lib/nova/instances"]["total"]
    assert res["type"] == "d"
    assert res["links"] == 2
    assert res["owner"] == "root"
    assert res["group"] == "root"
    assert res["se_user"] == "unconfined_u"
    assert res["se_role"] == "object_r"
    assert res["se_type"] == "var_lib_t"
    assert res["se_mls"] == "s0"
    assert res["date"] == "Apr  8 16:41"
    assert res["name"] == "abcd-efgh-ijkl-mnop"
    assert res["dir"] == "/var/lib/nova/instances"
