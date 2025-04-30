import doctest

from insights.parsers import ls_target_files
from insights.parsers.ls_target_files import LsTargetFiles
from insights.tests import context_wrap


LS_TARGET_FILES_DATA = """
{
  "/dev/sdb2": "brw-rw----. 1 0 6 252, 1 Apr 25 03:47 /dev/sdb2",
  "/dev/mapper/rhel-root": "brw-rw----. 1 0 6 252, 1 Apr 25 03:47 /dev/mapper/rhel-root",
  "/dev/mapper/rhel-home": "brw-rw----. 1 0 6 252, 1 Apr 25 03:47 /dev/mapper/rhel-home",
  "/dev/mapper/rhel-var": "brw-rw----. 1 0 6 252, 1 Apr 25 03:47 /dev/mapper/rhel-var",
  "/dev/vda1": "brw-rw----. 1 0 6 252, 1 Apr 25 03:47 /dev/vda1",
  "/dev/vda2": "brw-rw----. 1 0 6 252, 1 Apr 25 03:47 /dev/vda2"
}
""".strip()


def test_ls_target_files():
    ls_target_files_info = LsTargetFiles(context_wrap(LS_TARGET_FILES_DATA))
    assert ls_target_files_info.data["/dev/sdb2"] == "brw-rw----. 1 0 6 252, 1 Apr 25 03:47 /dev/sdb2"
    assert len(ls_target_files_info.data) == 6


def test_ls_target_files_doc():
    env = {
        'ls_target_files_info': LsTargetFiles(context_wrap(LS_TARGET_FILES_DATA))
    }
    failed, total = doctest.testmod(ls_target_files, globs=env)
    assert failed == 0
