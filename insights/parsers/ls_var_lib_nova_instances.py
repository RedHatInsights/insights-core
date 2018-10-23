'''
LsVarLibNovaInstances - command ``ls -laRZ /var/lib/nova/instances``
====================================================================

The ``ls -laRZ /var/lib/nova/instances`` command provides information for
the SELinux directory listing of the ``/var/lib/nova/instances`` directory.

Sample input is shown in the Examples. See ``FileListing`` class for
additional information.

Typical output of the ``ls -laRZ /var/lib/nova/instances`` command is::

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

Examples:

    >>> '/var/lib/nova/instances/' in ls_var_lib_nova_instances
    True
    >>> ls_var_lib_nova_instances.files_of('/var/lib/nova/instances/11415c6c-a2a5-45f0-a198-724246b96631')
    ['console.log', 'disk', 'disk.info']
    >>> ls_var_lib_nova_instances.listings['/var/lib/nova/instances/11415c6c-a2a5-45f0-a198-724246b96631']['entries']['console.log']['se_type'] != 'nova_var_lib_t'
    False
    >>> len(ls_var_lib_nova_instances.listings['/var/lib/nova/instances/locks'])
    6
    >>> ls_var_lib_nova_instances.dir_entry('/var/lib/nova/instances/locks', 'nova-storage-registry-lock')['raw_entry']
    '-rw-r--r--. nova nova system_u:object_r:nova_var_lib_t:s0 nova-storage-registry-lock'

'''


from insights import CommandParser, parser
from insights import FileListing
from insights.specs import Specs


@parser(Specs.ls_var_lib_nova_instances)
class LsVarLibNovaInstances(CommandParser, FileListing):
    '''
       Parses the output of ``ls -laRZ /var/lib/nova/instances``
       command which provides the SELinux directory listings of
       the '/var/lib/nova/instances' directory.
    '''
    pass
