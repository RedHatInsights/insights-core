import doctest

from insights.parsers import ls_run_systemd_generator
from insights.parsers.ls_run_systemd_generator import LsRunSystemdGenerator
from insights.tests import context_wrap

LS_RUN_SYSTEMD_GENERATOR = """
total 28
drwxr-xr-x.  6 0 0 260 Aug  5 07:35 .
drwxr-xr-x. 18 0 0 440 Aug  5 07:35 ..
-rw-r--r--.  1 0 0 254 Aug  5 07:35 boot.mount
-rw-r--r--.  1 0 0 259 Aug  5 07:35 boot\x2dfake.mount
-rw-r--r--.  1 0 0 176 Aug  5 07:35 dev-mapper-rhel\x2dswap.swap
drwxr-xr-x.  2 0 0 100 Aug  5 07:35 local-fs.target.requires
-rw-r--r--.  1 0 0 217 Aug  5 07:35 -.mount
drwxr-xr-x.  2 0 0  60 Aug  5 07:35 nfs-server.service.d
drwxr-xr-x.  2 0 0 100 Aug  5 07:35 remote-fs.target.requires
-rw-r--r--.  1 0 0 261 Aug  5 07:35 root-mnt_nfs3.mount
-rw-r--r--.  1 0 0 261 Aug  5 07:35 root-mnt\x2dnfs1.mount
-rw-r--r--.  1 0 0 261 Aug  5 07:35 root-mnt\x2dnfs2.mount
drwxr-xr-x.  2 0 0  60 Aug  5 07:35 swap.target.requires
""".strip()

PATH_OF_LS_RUN_SYSTEMD_GENERATOR = "insights_commands/ls_-lan_.run.systemd.generator"


def test_ls_run_systemd_generator():
    ls = LsRunSystemdGenerator(context_wrap(LS_RUN_SYSTEMD_GENERATOR,
                               path=PATH_OF_LS_RUN_SYSTEMD_GENERATOR))
    dir_path = "/run/systemd/generator"
    assert dir_path in ls
    assert len(ls.files_of(dir_path)) == 7
    assert ls.files_of(dir_path) == ['boot.mount', 'boot-fake.mount', 'dev-mapper-rhel-swap.swap',
                                '-.mount', 'root-mnt_nfs3.mount', 'root-mnt-nfs1.mount', 'root-mnt-nfs2.mount']
    assert ls.dirs_of(dir_path) == ['.', '..', 'local-fs.target.requires', 'nfs-server.service.d',
                               'remote-fs.target.requires', 'swap.target.requires']
    assert ls.listing_of(dir_path)['-.mount'] == {'type': '-', 'perms': 'rw-r--r--.', 'links': 1, 'owner': '0', 'group': '0', 'size': 217, 'date': 'Aug  5 07:35', 'name': '-.mount', 'raw_entry': '-rw-r--r--.  1 0 0 217 Aug  5 07:35 -.mount', 'dir': dir_path}


def test_ls_osroot_doc_examples():
    env = {
        'ls': LsRunSystemdGenerator(context_wrap(LS_RUN_SYSTEMD_GENERATOR,
                                    path=PATH_OF_LS_RUN_SYSTEMD_GENERATOR)),
    }
    failed, total = doctest.testmod(ls_run_systemd_generator, globs=env)
    assert failed == 0
