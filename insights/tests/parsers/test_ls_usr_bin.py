import doctest

from insights.core.filters import add_filter
from insights.parsers import ls_usr_bin
from insights.parsers.ls_usr_bin import LsUsrBin
from insights.specs import Specs
from insights.tests import context_wrap

LS_USR_BIN = """
total 41472
lrwxrwxrwx.  1 0  0        7 Oct 22  2019 python -> python2
-rwxr-xr-x.  1 0  0     2558 Apr 10  2019 python-argcomplete-check-easy-install-script
-rwxr-xr-x.  1 0  0      318 Apr 10  2019 python-argcomplete-tcsh
lrwxrwxrwx.  1 0  0       14 Oct 22  2019 python-config -> python2-config
lrwxrwxrwx.  1 0  0        9 Oct 22  2019 python2 -> python2.7
"""


def test_ls_usr_bin():
    ls_usr_bin = LsUsrBin(context_wrap(LS_USR_BIN, path='insights_commands/ls_-ln_.usr.bin'))
    assert ls_usr_bin.files_of('/usr/bin') == ['python', 'python-argcomplete-check-easy-install-script', 'python-argcomplete-tcsh', 'python-config', 'python2']
    python = ls_usr_bin.dir_entry('/usr/bin', 'python')
    assert python is not None
    assert python == {'date': 'Oct 22  2019',
        'dir': '/usr/bin',
        'group': '0',
        'link': 'python2',
        'links': 1,
        'name': 'python',
        'owner': '0',
        'perms': 'rwxrwxrwx.',
        'raw_entry': 'lrwxrwxrwx.  1 0  0        7 Oct 22  2019 python -> python2',
        'size': 7,
        'type': 'l'}


def test_ls_usr_bin_doc_examples():
    env = {
        'Specs': Specs,
        'add_filter': add_filter,
        'LsUsrBin': LsUsrBin,
        'ls_usr_bin': LsUsrBin(context_wrap(LS_USR_BIN, path='insights_commands/ls_-ln_.usr.bin')),
    }
    failed, total = doctest.testmod(ls_usr_bin, globs=env)
    assert failed == 0
