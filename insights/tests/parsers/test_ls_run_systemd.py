import doctest

from insights.parsers import ls_run_systemd
from insights.parsers.ls_run_systemd import LsRunSystemd
from insights.tests import context_wrap


# command output is shortened
LS_RUN_SYSTEMD = """
/run/systemd:
total 0
drwxr-xr-x. 16 0 0  400 May 25 09:03 .
drwxr-xr-x. 33 0 0  940 May 25 09:03 ..
srwx------.  1 0 0    0 May 25 09:03 cgroups-agent
srw-------.  1 0 0    0 May 25 09:03 coredump
drwxr-xr-x.  4 0 0  140 May 25 09:03 generator
d---------.  3 0 0  160 May 25 09:03 inaccessible
srwxrwxrwx.  1 0 0    0 May 25 09:03 notify
srwxrwxrwx.  1 0 0    0 May 25 09:03 private
drwxr-xr-x.  2 0 0   40 May 25 09:03 system
drwxr-xr-x.  2 0 0  100 May 25 09:17 transient

/run/systemd/generator:
total 12
drwxr-xr-x.  4 0 0 140 May 25 09:03 .
drwxr-xr-x. 16 0 0 400 May 25 09:03 ..
-rw-r--r--.  1 0 0 254 May 25 09:03 boot.mount
-rw-r--r--.  1 0 0 230 May 25 09:03 dev-mapper-rhel\x2dswap.swap
drwxr-xr-x.  2 0 0  80 May 25 09:03 local-fs.target.requires
-rw-r--r--.  1 0 0 217 May 25 09:03 -.mount
drwxr-xr-x.  2 0 0  60 May 25 09:03 swap.target.requires

/run/systemd/generator/local-fs.target.requires:
total 8
drwxr-xr-x. 2 0 0  80 May 25 09:03 .
drwxr-xr-x. 4 0 0 140 May 25 09:03 ..
-rw-r--r--. 1 0 0 254 May 25 09:03 boot.mount
-rw-r--r--. 1 0 0 217 May 25 09:03 -.mount

/run/systemd/generator/swap.target.requires:
total 4
drwxr-xr-x. 2 0 0  60 May 25 09:03 .
drwxr-xr-x. 4 0 0 140 May 25 09:03 ..
-rw-r--r--. 1 0 0 230 May 25 09:03 dev-mapper-rhel\x2dswap.swap

/run/systemd/system:
total 0
drwxr-xr-x.  2 0 0  40 May 25 09:03 .
drwxr-xr-x. 16 0 0 400 May 25 09:03 ..

/run/systemd/transient:
total 12
drwxr-xr-x.  2 0 0 100 May 25 09:17 .
drwxr-xr-x. 16 0 0 400 May 25 09:03 ..
-rw-r--r--.  1 0 0 275 May 25 09:04 session-6.scope
-rw-r--r--.  1 0 0 275 May 25 09:17 session-7.scope
-rw-r--r--.  1 0 0 275 May 25 09:17 session-8.scope
""".strip()


def test_ls_run_systemd():
    run_systemd = LsRunSystemd(context_wrap(LS_RUN_SYSTEMD))
    assert run_systemd
    assert len(run_systemd.listings) == 6
    assert run_systemd.dirs_of("/run/systemd/generator") == [
        '.', '..', 'local-fs.target.requires', 'swap.target.requires'
    ]
    assert run_systemd.files_of("/run/systemd/generator") == [
        'boot.mount', 'dev-mapper-rhel-swap.swap', '-.mount'
    ]
    assert run_systemd.listing_of("/run/systemd/generator")['-.mount'] == {
        'date': 'May 25 09:03', 'dir': '/run/systemd/generator', 'group': '0', 'links': 1,
        'name': '-.mount', 'owner': '0', 'perms': 'rw-r--r--.',
        'raw_entry': '-rw-r--r--.  1 0 0 217 May 25 09:03 -.mount', 'size': 217, 'type': '-'
    }


def test_ls_osroot_doc_examples():
    env = {
        'ls_run_systemd': LsRunSystemd(context_wrap(LS_RUN_SYSTEMD))
    }
    failed, total = doctest.testmod(ls_run_systemd, globs=env)
    assert failed == 0
