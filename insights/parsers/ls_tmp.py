"""
LsTmp - Command ``ls -la /tmp``
===============================

The ``ls -la /tmp`` command provides information for the listing of the
``/tmp`` directory.

"""
from insights import parser, FileListing, CommandParser
from insights.specs import Specs


@parser(Specs.ls_tmp)
class LsTmp(CommandParser, FileListing):
    """
    Parses output of ``ls -lan /tmp`` command.  See ``FileListing`` class for
    additional information.

    To prevent the output content from being too large, filters should be
    applied.  Sample output of ``ls -lan /tmp`` after filtered::

        drwxrwxr-x.  2 whuser   whuser         216 Jul  9 07:09 aws_sos
        -rw-r--r--.  1 rauser   rauser        1123 Jul 10 00:00 clean-old-archive.log
        -rw-rw-r--.  1 whuser   whuser        9620 Jul  9 07:09 daily-extraction-warehouse-run.log
        -rw-rw-r--.  1 whuser   whuser       11214 Jul  9 07:09 dask_master.log
        -rw-rw-r--.  1 whuser   whuser       27091 Jul  9 07:09 dask_worker.log
        -rw-r--r--.  1 user10   user10          29 Jul 10 00:00 date.out
        -rw-r--r--.  1 rauser   rauser   325933528 Jul 10 00:18 delete-bad-pods.log
        -rw-rw-r--.  1 whuser   whuser           0 Jul  9 07:08 extraction_driver.log
        drwxrwxrwt.  2 root     root             6 Mar 27  2017 .font-unix
        drwxrwxr-x.  3 user1    user1           17 Oct 28  2019 hadoop-user1
        drwxr-xr-x.  2 user1    user1           32 Jul  4 18:29 hsperfdata_user1
        drwxr-xr-x.  2 rauser   rauser           6 Jul 10 00:00 hsperfdata_rauser
        drwxr-xr-x.  2 root     root             6 Jul  1 14:53 hsperfdata_root
        drwxrwxrwt.  2 root     root             6 Mar 27  2017 .ICE-unix
        srw-rw----.  1 user10   user10           0 Jan  6  2020 lh_pair
        srw-rw----.  1 user10   user10           0 Jan 28 11:24 lh_pair_ex


    Examples:
        >>> type(ls_tmp)
        <class 'insights.parsers.ls_tmp.LsTmp'>
        >>> len(ls_tmp.files_of("/tmp"))
        9
        >>> len(ls_tmp.dirs_of("/tmp"))
        7
        >>> "/tmp" in ls_tmp
        True
        >>> "aws_sos" in ls_tmp.dirs_of("/tmp")
        True
        >>> "aws_sos" not in ls_tmp.files_of("/tmp")
        True
        >>> "date.out" not in ls_tmp.dirs_of("/tmp")
        True
        >>> "date.out" in ls_tmp.files_of("/tmp")
        True
    """
    pass
