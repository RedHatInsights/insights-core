"""
LsVarTmp - command ``ls -lanR /var/tmp``
========================================

The ``ls -lanR /var/tmp`` command provides information for the listing of the
``/var/tmp`` directory.

Sample input is shown in the Examples. See ``FileListing`` class for
additional information.

Sample directory list::

    /var/tmp:
    total 20
    drwxrwxrwt.  5 0 0 4096 Apr 28  2018 .
    drwxr-xr-x. 24 0 0 4096 Oct 15  2015 ..
    drwxr-xr-x.  2 0 0 4096 Mar 26 02:25 a1
    drwxr-xr-x.  2 0 0 4096 Mar 26 02:25 a2
    drwxr-xr-x.  2 0 0 4096 Apr 28  2018 foreman-ssh-cmd-fc3f65c9-2b35-480d-87e3-1d971433d6ad

    /var/tmp/a1:
    total 8
    drwxr-xr-x. 2 0 0 4096 Mar 26 02:25 .
    drwxrwxrwt. 5 0 0 4096 Apr 28  2018 ..

    /var/tmp/a2:
    total 8
    drwxr-xr-x. 2 0 0 4096 Mar 26 02:25 .
    drwxrwxrwt. 5 0 0 4096 Apr 28  2018 ..

    /var/tmp/foreman-ssh-cmd-fc3f65c9-2b35-480d-87e3-1d971433d6ad:
    total 36
    drwxr-xr-x. 3 0 0  4096 Apr  3 02:50 .
    drwxrwxrwt. 5 0 0  4096 Apr 28  2018 ..
    drwxr-xr-x. 2 0 0  4096 Apr  3 02:50 dir1
    -rw-r--r--. 1 0 0     2 Apr 28  2018 exit_code
    -rw-r--r--. 1 0 0 15606 Apr 28  2018 output
    -rwxr-xr-x. 1 0 0    14 Apr 28  2018 script
    -rw-r--r--. 1 0 0     0 Apr  3 02:50 test

    /var/tmp/foreman-ssh-cmd-fc3f65c9-2b35-480d-87e3-1d971433d6ad/dir1:
    total 8
    drwxr-xr-x. 2 0 0 4096 Apr  3 02:50 .
    drwxr-xr-x. 3 0 0 4096 Apr  3 02:50 ..


Examples:

    >>> "a1" in ls_var_tmp
    False
    >>> "/var/tmp/a1" in ls_var_tmp
    True
    >>> ls_var_tmp.files_of("/var/tmp/foreman-ssh-cmd-fc3f65c9-2b35-480d-87e3-1d971433d6ad")
    ['exit_code', 'output', 'script', 'test']
    >>> ls_var_tmp.dirs_of("/var/tmp/foreman-ssh-cmd-fc3f65c9-2b35-480d-87e3-1d971433d6ad")
    ['.', '..', 'dir1']
    >>> ls_var_tmp.total_of("/var/tmp/foreman-ssh-cmd-fc3f65c9-2b35-480d-87e3-1d971433d6ad")
    36
"""


from insights.specs import Specs

from .. import FileListing
from .. import parser


@parser(Specs.ls_var_tmp)
class LsVarTmp(FileListing):
    """Parses output of ``ls -lanR /var/tmp`` command."""
    pass
