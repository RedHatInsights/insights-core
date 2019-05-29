import doctest
from insights.parsers import nova_libvirt_ls_root as ls_root
from insights.tests import context_wrap


NOVA_LIBVIRT_LS_ROOT = """
/root:
total 48
dr-xr-x---. 1 0 0   53 May 28 07:53 .
drwxr-xr-x. 1 0 0   59 Jul 14  2018 ..
-rw-------. 1 0 0  176 May 23 11:29 .bash_history
drwx------. 2 0 0   20 May 29 05:32 .ssh
-rw-r--r--. 1 0 0   18 Dec 29  2013 .bash_logout
-rw-r--r--. 1 0 0  176 Dec 29  2013 .bash_profile
-rw-r--r--. 1 0 0  325 Jun 15  2018 .bashrc
-rw-r--r--. 1 0 0  100 Dec 29  2013 .cshrc
-rw-------. 1 0 0 4790 May 23  2018 anaconda-ks.cfg
drwxr-xr-x. 1 0 0   63 Jun 21  2018 buildinfo
-rw-------. 1 0 0  124 May 28 07:53 config

/root/.ssh:
total 4
drwx------. 2 0 0  20 May 29 05:32 .
drwxr-xr-x. 8 0 0 110 Jun 21  2018 ..
-rw-------. 1 0 0 124 Jul 14  2018 config

/root/buildinfo:
total 24
drwxr-xr-x. 1 0 0    63 Jun 21  2018 .
dr-xr-x---. 1 0 0    53 May 28 07:53 ..
-rw-r--r--. 1 0 0  2732 May 23  2018 Dockerfile-rhel7-7.5-245.1527091554
-rw-r--r--. 1 0 0 12376 Jun 15  2018 Dockerfile-rhosp13-openstack-base-13.0-62
-rw-r--r--. 1 0 0  1635 Jun 21  2018 Dockerfile-rhosp13-openstack-nova-libvirt-13.0-43
""".strip()


def test_nova_libvirt_ls_root():
    ls = ls_root.NovaLibvirtLsRoot(context_wrap(NOVA_LIBVIRT_LS_ROOT))
    assert ls.dirs_of('/root/.ssh') == ['.', '..']
    assert ls.listings['/root/buildinfo']['entries']['Dockerfile-rhel7-7.5-245.1527091554']['perms'] == 'rw-r--r--.'
    assert ls.listings['/root/.ssh']['entries']['config']['links']


def test_nova_libvirt_ls_root_doc_examples():
    failed, total = doctest.testmod(
        ls_root,
        globs={'ls': ls_root.NovaLibvirtLsRoot(context_wrap(NOVA_LIBVIRT_LS_ROOT))}
    )
    assert failed == 0
