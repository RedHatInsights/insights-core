import doctest
from insights.parsers import ls_var_lib_nova_instances
from insights.parsers.ls_var_lib_nova_instances import LsVarLibNovaInstances
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


def test_ls_var_lib_nova_instances():
    ls_var_lib_nova_instances = LsVarLibNovaInstances(context_wrap(LS_VAR_LIB_NOVA_INSTANCES))
    assert ls_var_lib_nova_instances.dirs_of('/var/lib/nova/instances/') == ['.', '..', '11415c6c-a2a5-45f0-a198-724246b96631', '_base', 'locks']
    assert ls_var_lib_nova_instances.listings['/var/lib/nova/instances/11415c6c-a2a5-45f0-a198-724246b96631']['entries']['console.log']['se_type'] == 'nova_var_lib_t'
    assert ls_var_lib_nova_instances.dir_entry('/var/lib/nova/instances/locks', 'nova-storage-registry-lock') == {'se_type': 'nova_var_lib_t', 'name': 'nova-storage-registry-lock', 'perms': 'rw-r--r--.', 'se_user': 'system_u', 'raw_entry': '-rw-r--r--. nova nova system_u:object_r:nova_var_lib_t:s0 nova-storage-registry-lock', 'se_mls': 's0', 'se_role': 'object_r', 'owner': 'nova', 'group': 'nova', 'type': '-', 'dir': '/var/lib/nova/instances/locks'}
    assert ls_var_lib_nova_instances.dir_entry('/var/lib/nova/instances/11415c6c-a2a5-45f0-a198-724246b96631', 'console.log')['owner'] == 'root'


def test_ls_var_lib_nova_instances_doc_examples():
    env = {
        'LsVarLibNovaInstances': LsVarLibNovaInstances,
        'ls_var_lib_nova_instances': LsVarLibNovaInstances(context_wrap(LS_VAR_LIB_NOVA_INSTANCES)),
    }
    failed, total = doctest.testmod(ls_var_lib_nova_instances, globs=env)
    assert failed == 0
