from insights.parsers.ls_etc_ssh import LsEtcSsh
from insights.tests import context_wrap
from insights.parsers import ls_etc_ssh
import doctest

LS_ETC_SSH = """
total 612
drwxr-xr-x.   3 0   0    245 Aug 11 14:19 .
drwxr-xr-x. 138 0   0   8192 Jul 29 19:11 ..
-rw-r--r--.   1 0   0 577388 Mar 27  2020 moduli
-rw-r--r--.   1 0   0   1770 Mar 27  2020 ssh_config
drwxr-xr-x.   2 0   0     28 May 12 17:10 ssh_config.d
-rw-r-----.   1 0 994    480 May 13 09:58 ssh_host_ecdsa_key
-rw-r--r--.   1 0   0    162 May 13 09:58 ssh_host_ecdsa_key.pub
-rw-r-----.   1 0 994    387 May 13 09:58 ssh_host_ed25519_key
-rw-r--r--.   1 0   0     82 May 13 09:58 ssh_host_ed25519_key.pub
-rw-r-----.   1 0 994   2578 May 13 09:58 ssh_host_rsa_key
-rw-r--r--.   1 0   0    554 May 13 09:58 ssh_host_rsa_key.pub
-rw-------.   1 0   0   4260 Aug 11 14:19 sshd_config
"""


def test_ls_etc_ssh():
    ls_etc_ssh = LsEtcSsh(context_wrap(LS_ETC_SSH, path='ls_-lanL_.etc.ssh'))
    assert '/etc/ssh' in ls_etc_ssh
    assert len(ls_etc_ssh.files_of("/etc/ssh")) == 9
    assert ls_etc_ssh.files_of("/etc/ssh") == ['moduli', 'ssh_config', 'ssh_host_ecdsa_key', 'ssh_host_ecdsa_key.pub', 'ssh_host_ed25519_key', 'ssh_host_ed25519_key.pub', 'ssh_host_rsa_key', 'ssh_host_rsa_key.pub', 'sshd_config']
    assert ls_etc_ssh.dirs_of("/etc/ssh") == ['.', '..', 'ssh_config.d']
    assert ls_etc_ssh.listing_of("/etc/ssh")['ssh_host_rsa_key'] == {'group': '994', 'name': 'ssh_host_rsa_key', 'links': 1, 'perms': 'rw-r-----.', 'raw_entry': '-rw-r-----.   1 0 994   2578 May 13 09:58 ssh_host_rsa_key', 'owner': '0', 'date': 'May 13 09:58', 'type': '-', 'dir': '/etc/ssh', 'size': 2578}


def test_ls_etc_ssh_doc_examples():
    env = {'ls_etc_ssh': LsEtcSsh(context_wrap(LS_ETC_SSH, path='ls_-lanL_.etc.ssh'))}
    failed, total = doctest.testmod(ls_etc_ssh, globs=env)
    assert failed == 0
