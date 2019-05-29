import doctest
from insights.parsers import nova_compute_var_lib_nova as ls_var_lib_nova
from insights.tests import context_wrap


NOVA_COMPUTE_LS_VAR_LIB_NOVA = """
total 4
drwxr-xr-x. 2 42436 42436   6 Jun 21  2018 tmp
drwxr-xr-x. 2 42436 42436   6 Jun 21  2018 networks
drwxr-xr-x. 2 42436 42436   6 Jun 21  2018 keys
drwxr-xr-x. 5 42436 42436  97 May 23 10:42 instances
drwxr-xr-x. 2 42436 42436   6 Jun 21  2018 buckets
drwx------. 2 42436 42436  20 May 28 09:34 .ssh
-rw-------. 1 42436 42436 682 May 27 11:12 .bash_history
drwxr-xr-x. 1     0     0  19 Jul 14  2018 ..
drwxr-xr-x. 8 42436 42436 110 Jun 21  2018 .
""".strip()


def test_nova_compute_ls_var_lib_nova():
    ls = ls_var_lib_nova.NovaComputeLsVarLibNova(context_wrap(NOVA_COMPUTE_LS_VAR_LIB_NOVA, path="insights_commands/docker_exec_nova_compute_.bin.ls_-larn_.var.lib.nova"))
    assert ls.files_of("/var/lib/nova") == ['.bash_history']
    assert ls.dirs_of("/var/lib/nova") == ['tmp', 'networks', 'keys', 'instances', 'buckets', '.ssh', '..', '.']
    assert ls.listing_of("/var/lib/nova")[".ssh"]["owner"] == '42436'


def test_nova_compute_ls_var_lib_nova_doc_examples():
    failed, total = doctest.testmod(
        ls_var_lib_nova,
        globs={'ls': ls_var_lib_nova.NovaComputeLsVarLibNova(context_wrap(NOVA_COMPUTE_LS_VAR_LIB_NOVA, path="insights_commands/docker_exec_nova_compute_.bin.ls_-larn_.var.lib.nova"))}
    )
    assert failed == 0
