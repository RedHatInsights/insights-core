from falafel.mappers.ls_var_log import LsVarLog
from falafel.tests import context_wrap
from falafel.util.file_permissions import FilePermissions

# from RHEL 7.2
LS_1 = """
/var/log:
total 1016
drwxr-xr-x.  7 root root   4096 Oct 19 15:38 .
drwxr-xr-x. 19 root root   4096 Oct 19 15:38 ..
drwxr-xr-x.  2 root root   4096 Jun 28 10:26 anaconda
drwxr-x---.  2 root root     22 Jun 28 10:26 audit
-rw-r--r--.  1 root root   8433 Oct 19 15:38 boot.log
-rw-------.  1 root utmp      0 Oct 19 05:39 btmp
-rw-------.  1 root root  11370 Oct 19 22:01 cron
-rw-r--r--.  1 root root  32226 Oct 19 15:38 dmesg
-rw-r--r--.  1 root root  34423 Oct 19 15:27 dmesg.old
-rw-------.  1 root root   5466 Oct 19 05:40 grubby
-rw-r--r--.  1 root root 292292 Oct 19 22:42 lastlog
-rw-------.  1 root root   1386 Oct 19 15:39 maillog
-rw-------.  1 root root 609617 Oct 19 22:42 messages
drwx------.  2 root root      6 Jan 26  2014 ppp
drwxr-xr-x.  2 root root     41 Jun 28 10:28 rhsm
-rw-------.  1 root root  18185 Oct 19 22:42 secure
-rw-------.  1 root root      0 Jun 28 10:20 spooler
-rw-------.  1 root root      0 Jun 28 10:19 tallylog
drwxr-xr-x.  2 root root     22 Sep  1 07:32 tuned
-rw-r--r--.  1 root root   1854 Oct 19 22:38 up2date
-rw-r--r--.  1 root root 211784 Jun 28 10:41 vboxadd-install.log
-rw-r--r--.  1 root root     73 Oct 19 05:17 vboxadd-install-x11.log
-rw-r--r--.  1 root root      1 Jun 28 10:40 VBoxGuestAdditions.log
-rw-r--r--.  1 root root    280 Oct 19 15:38 wpa_supplicant.log
-rw-rw-r--.  1 root utmp  21504 Oct 19 22:42 wtmp
-rw-------.  1 root root   8423 Oct 19 15:29 yum.log

/var/log/anaconda:
total 1048
drwxr-xr-x. 2 root root   4096 Jun 28 10:26 .
drwxr-xr-x. 7 root root   4096 Oct 19 15:38 ..
-rw-------. 1 root root  17862 Jun 28 10:26 anaconda.log
-rw-------. 1 root root   1726 Jun 28 10:26 ifcfg.log
-rw-------. 1 root root 680224 Jun 28 10:26 journal.log
-rw-------. 1 root root      0 Jun 28 10:26 ks-script-2aaku7.log
-rw-------. 1 root root 114262 Jun 28 10:26 packaging.log
-rw-------. 1 root root  30137 Jun 28 10:26 program.log
-rw-------. 1 root root  88243 Jun 28 10:26 storage.log
-rw-------. 1 root root  63190 Jun 28 10:26 syslog
-rw-------. 1 root root  52756 Jun 28 10:26 X.log

/var/log/audit:
total 1288
drwxr-x---. 2 root root      22 Jun 28 10:26 .
drwxr-xr-x. 7 root root    4096 Oct 19 15:38 ..
-rw-------. 1 root root 1259137 Oct 19 22:42 audit.log

/var/log/ppp:
total 4
drwx------. 2 root root    6 Jan 26  2014 .
drwxr-xr-x. 7 root root 4096 Oct 19 15:38 ..

/var/log/rhsm:
total 32
drwxr-xr-x. 2 root root    41 Jun 28 10:28 .
drwxr-xr-x. 7 root root  4096 Oct 19 15:38 ..
-rw-r--r--. 1 root root  4279 Oct 19 19:39 rhsmcertd.log
-rw-r--r--. 1 root root 18331 Oct 19 19:39 rhsm.log

/var/log/tuned:
total 16
drwxr-xr-x. 2 root root   22 Sep  1 07:32 .
drwxr-xr-x. 7 root root 4096 Oct 19 15:38 ..
-rw-r--r--. 1 root root 8834 Oct 19 15:39 tuned.log

""".strip()


def test_smoketest():
    context = context_wrap(LS_1)
    result = LsVarLog(context)

    assert "/var/log:" in result.lines_unparsed
    assert "-rw-r--r--. 1 root root 8834 Oct 19 15:39 tuned.log" in result.lines_unparsed
    assert "/var/log" in result.dir_parsed
    assert "/var/log/audit" in result.dir_parsed
    assert "/var/log/ppp" in result.dir_parsed
    assert "/var/log/rhsm" in result.dir_parsed
    assert "/var/log/tuned" in result.dir_parsed
    assert "audit.log" == result.dir_parsed["/var/log/audit"][2].path
    assert "audit.log" == result.get_filepermissions("/var/log/audit", "audit.log").path


def test_lines_unparsed():
    context = context_wrap(LS_1)
    result = LsVarLog(context)
    test_lines = LS_1.split("\n")
    assert test_lines == result.lines_unparsed


def test_dir_parsed():
    context = context_wrap(LS_1)
    result = LsVarLog(context)
    ls = {}
    current_dir = ""
    test_lines = LS_1.split("\n")
    for line in test_lines:
        # wonky parsing from memory to test the actual implementation; doesn't expect evil input!
        if line.endswith(":"):
            current_dir = line.split(":")[0]
            ls[current_dir] = []
        elif line.startswith("total"):
            pass
        elif line:
            fileperm = FilePermissions(line)
            ls[current_dir].append(fileperm)
    for dir in ls:
        assert dir in result.dir_parsed
        test_list = []
        result_list = []
        for fil in ls[dir]:
            # saving FilePermissions().line
            test_list.append(fil.line)
        for fil in result.dir_parsed[dir]:
            # saving FilePermissions().line
            result_list.append(fil.line)
        # comparing the "line" attributes of the FilePermissions instances
        assert test_list == result_list


def test_get_filepermissions():
    context = context_wrap(LS_1)
    result = LsVarLog(context)
    ls = {}
    current_dir = ""
    test_lines = LS_1.split("\n")
    for line in test_lines:
        # wonky parsing from memory to test the actual implementation; doesn't expect evil input!
        if line.endswith(":"):
            current_dir = line.split(":")[0]
            ls[current_dir] = []
        elif line.startswith("total"):
            pass
        elif line:
            fileperm = FilePermissions(line)
            ls[current_dir].append(fileperm)
    for dir in ls:
        assert dir in result.dir_parsed
        for fil in ls[dir]:
            found = result.get_filepermissions(dir, fil.path)
            assert found is not None
            assert fil.line == found.line
            not_found = result.get_filepermissions(dir, "nonexisting" + fil.path)
            assert not_found is None
