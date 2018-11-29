import doctest
from insights.parsers import ls_var_lib_nova_instances as ls_instances
from insights.tests import context_wrap


LS_VAR_LIB_NOVA_INSTANCES = '''
/var/lib/nova/instances/:
drwxr-xr-x. nova nova system_u:object_r:nova_var_lib_t:s0 .
drwxr-xr-x. nova nova system_u:object_r:nova_var_lib_t:s0 ..
drwxr-xr-x. nova nova system_u:object_r:nova_var_lib_t:s0 11415c6c-a2a5-45f0-a198-724246b96631
drwxr-xr-x. nova nova system_u:object_r:nova_var_lib_t:s0 _base
-rw-r--r--. nova nova system_u:object_r:nova_var_lib_t:s0 compute_nodes
drwxr-xr-x. nova nova system_u:object_r:nova_var_lib_t:s0 locks

/var/lib/nova/instances/11415c6c-a2a5-45f0-a198-724246b96631:
drwxr-xr-x. nova nova system_u:object_r:nova_var_lib_t:s0 .
drwxr-xr-x. nova nova system_u:object_r:nova_var_lib_t:s0 ..
-rw-------. root root system_u:object_r:nova_var_lib_t:s0 console.log
-rw-r--r--. qemu qemu system_u:object_r:svirt_image_t:s0:c92,c808 disk
-rw-r--r--. nova nova system_u:object_r:nova_var_lib_t:s0 disk.info

/var/lib/nova/instances/_base:
drwxr-xr-x. nova nova system_u:object_r:nova_var_lib_t:s0 .
drwxr-xr-x. nova nova system_u:object_r:nova_var_lib_t:s0 ..
-rw-r--r--. qemu qemu system_u:object_r:virt_content_t:s0 572dfdb7e1d9304342cbe1fd5e3da4ff2e55c7a6

/var/lib/nova/instances/locks:
drwxr-xr-x. nova nova system_u:object_r:nova_var_lib_t:s0 .
drwxr-xr-x. nova nova system_u:object_r:nova_var_lib_t:s0 ..
-rw-r--r--. nova nova system_u:object_r:nova_var_lib_t:s0 nova-572dfdb7e1d9304342cbe1fd5e3da4ff2e55c7a6
-rw-r--r--. nova nova system_u:object_r:nova_var_lib_t:s0 nova-storage-registry-lock
'''.strip()


LS_R_VAR_LIB_NOVA_INSTANCES = '''
/var/lib/nova/instances:
total 4
drwxr-xr-x. 5 nova nova  97 Feb 20  2017 .
drwxr-xr-x. 9 nova nova 111 Feb 17  2017 ..
drwxr-xr-x. 2 nova nova  54 Feb 17  2017 _base
-rw-r--r--. 1 nova nova  44 May 26  2017 compute_nodes
drwxr-xr-x. 2 nova nova  54 Feb 17  2017 e560e649-41fd-46a2-a3d2-5f4750ba2bb4
drwxr-xr-x. 2 nova nova  93 Feb 17  2017 locks

/var/lib/nova/instances/_base:
total 18176
drwxr-xr-x. 2 nova nova       54 Feb 17  2017 .
drwxr-xr-x. 5 nova nova       97 Feb 20  2017 ..
-rw-r--r--. 1 qemu qemu 41126400 May 26  2017 faf1184c098da91e90290a920b8fab1ee6e1d4c4

/var/lib/nova/instances/e560e649-41fd-46a2-a3d2-5f4750ba2bb4:
total 2104
drwxr-xr-x. 2 nova nova      54 Feb 17  2017 .
drwxr-xr-x. 5 nova nova      97 Feb 20  2017 ..
-rw-r--r--. 1 qemu qemu   48957 Feb 20  2017 console.log
-rw-r--r--. 1 qemu qemu 2097152 Feb 20  2017 disk
-rw-r--r--. 1 nova nova      79 Feb 17  2017 disk.info

/var/lib/nova/instances/locks:
total 0
drwxr-xr-x. 2 nova nova 93 Feb 17  2017 .
drwxr-xr-x. 5 nova nova 97 Feb 20  2017 ..
-rw-r--r--. 1 nova nova  0 Feb 17  2017 nova-faf1184c098da91e90290a920b8fab1ee6e1d4c4
-rw-r--r--. 1 nova nova  0 Feb 17  2017 nova-storage-registry-lock
'''.strip()


def test_ls_var_lib_nova_instances():
    ls_var_lib_nova_instances = ls_instances.LsVarLibNovaInstances(context_wrap(LS_VAR_LIB_NOVA_INSTANCES))
    assert ls_var_lib_nova_instances.dirs_of('/var/lib/nova/instances/') == ['.', '..', '11415c6c-a2a5-45f0-a198-724246b96631', '_base', 'locks']
    assert ls_var_lib_nova_instances.listings['/var/lib/nova/instances/11415c6c-a2a5-45f0-a198-724246b96631']['entries']['console.log']['se_type'] == 'nova_var_lib_t'
    assert ls_var_lib_nova_instances.dir_entry('/var/lib/nova/instances/locks', 'nova-storage-registry-lock') == {'se_type': 'nova_var_lib_t', 'name': 'nova-storage-registry-lock', 'perms': 'rw-r--r--.', 'se_user': 'system_u', 'raw_entry': '-rw-r--r--. nova nova system_u:object_r:nova_var_lib_t:s0 nova-storage-registry-lock', 'se_mls': 's0', 'se_role': 'object_r', 'owner': 'nova', 'group': 'nova', 'type': '-', 'dir': '/var/lib/nova/instances/locks'}
    assert ls_var_lib_nova_instances.dir_entry('/var/lib/nova/instances/11415c6c-a2a5-45f0-a198-724246b96631', 'console.log')['owner'] == 'root'


def test_ls_r_var_lib_nova_instances():
    ls_r_instances = ls_instances.LsRVarLibNovaInstances(context_wrap(LS_R_VAR_LIB_NOVA_INSTANCES))
    assert ls_r_instances.dir_entry('/var/lib/nova/instances/e560e649-41fd-46a2-a3d2-5f4750ba2bb4', 'console.log')['size'] == 48957


def test_ls_var_lib_nova_instances_doc_examples():
    failed, total = doctest.testmod(
        ls_instances,
        globs={'ls_var_lib_nova_instances': ls_instances.LsVarLibNovaInstances(context_wrap(LS_VAR_LIB_NOVA_INSTANCES)),
               'ls_r_var_lib_nova_instances': ls_instances.LsRVarLibNovaInstances(context_wrap(LS_R_VAR_LIB_NOVA_INSTANCES))}
    )
    assert failed == 0
