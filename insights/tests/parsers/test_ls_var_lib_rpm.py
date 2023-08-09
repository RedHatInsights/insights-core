from insights.parsers import ls_var_lib_rpm
from insights.parsers.ls_var_lib_rpm import LsVarLibRpm
from insights.tests import context_wrap
import doctest

LS_VAR_LIB_RPM = """
total 172400
drwxr-xr-x.  2 0 0      4096 Oct 19  2022 .
drwxr-xr-x. 31 0 0      4096 Nov 26  2021 ..
-rw-r--r--.  1 0 0   4034560 Apr 17 16:06 Basenames
-rw-r--r--.  1 0 0      8192 Apr 17 16:06 Conflictname
-rw-r--r--.  1 0 0    270336 Apr 24 10:31 __db.001
-rw-r--r--.  1 0 0     81920 Apr 24 10:31 __db.002
-rw-r--r--.  1 0 0   1318912 Apr 24 10:31 __db.003
-rw-r--r--.  1 0 0         0 Nov  9  2021 .dbenv.lock
-rw-r--r--.  1 0 0   2707456 Apr 17 16:06 Dirnames
-rw-r--r--.  1 0 0      8192 Nov  9  2021 Enhancename
-rw-r--r--.  1 0 0      8192 Nov 26  2021 Filetriggername
-rw-r--r--.  1 0 0     12288 Apr 17 16:06 Group
-rw-r--r--.  1 0 0     20480 Apr 17 16:06 Installtid
-rw-r--r--.  1 0 0     45056 Apr 17 16:06 Name
-rw-r--r--.  1 0 0     16384 Apr 17 10:43 Obsoletename
-rw-r--r--.  1 0 0 165253120 Apr 17 16:06 Packages
-rw-r--r--.  1 0 0   2461696 Apr 17 16:06 Providename
-rw-r--r--.  1 0 0      8192 Apr 17 10:42 Recommendname
-rw-r--r--.  1 0 0    245760 Apr 17 16:06 Requirename
-rw-r--r--.  1 0 0         0 Nov  9  2021 .rpm.lock
-rw-r--r--.  1 0 0     77824 Apr 17 16:06 Sha1header
-rw-r--r--.  1 0 0     40960 Apr 17 16:06 Sigmd5
-rw-r--r--.  1 0 0      8192 Apr 17 10:42 Suggestname
-rw-r--r--.  1 0 0      8192 Apr 17 10:42 Supplementname
-rw-r--r--.  1 0 0      8192 Apr 17 10:42 Transfiletriggername
-rw-r--r--.  1 0 0      8192 Apr 17 10:44 Triggername
"""

LS_VAR_LIB_RPM_DOC_EXAMPLE = """
total 172400
drwxr-xr-x.  2 0 0      4096 Oct 19  2022 .
drwxr-xr-x. 31 0 0      4096 Nov 26  2021 ..
-rw-r--r--.  1 0 0   4034560 Apr 17 16:06 Basenames
-rw-r--r--.  1 0 0      8192 Apr 17 16:06 Conflictname
-rw-r--r--.  1 0 0     16384 Apr 17 10:43 Obsoletename
-rw-r--r--.  1 0 0 165253120 Apr 17 16:06 Packages
-rw-r--r--.  1 0 0   2461696 Apr 17 16:06 Providename
-rw-r--r--.  1 0 0      8192 Apr 17 10:42 Recommendname
"""


def test_ls_var_lib_rpm():
    var_lib_rpm = LsVarLibRpm(context_wrap(LS_VAR_LIB_RPM, path="insights_commands/ls_-lan_.var.lib.rpm"))
    assert len(var_lib_rpm.files_of('/var/lib/rpm')) == 24
    assert 'Recommendname' in var_lib_rpm.files_of('/var/lib/rpm')
    assert var_lib_rpm.dir_contains('/var/lib/rpm', 'Packages') is True
    assert var_lib_rpm.dir_entry('/var/lib/rpm', 'Triggername') == {'type': '-', 'perms': 'rw-r--r--.', 'links': 1, 'owner': '0', 'group': '0', 'size': 8192, 'date': 'Apr 17 10:44', 'name': 'Triggername', 'raw_entry': '-rw-r--r--.  1 0 0      8192 Apr 17 10:44 Triggername', 'dir': '/var/lib/rpm'}


def test_ls_var_lib_rpm_doc_examples():
    env = {
        'var_lib_rpm': LsVarLibRpm(context_wrap(LS_VAR_LIB_RPM_DOC_EXAMPLE, path="insights_commands/ls_-lan_.var.lib.rpm"))
           }
    failed, total = doctest.testmod(ls_var_lib_rpm, globs=env)
    assert failed == 0
