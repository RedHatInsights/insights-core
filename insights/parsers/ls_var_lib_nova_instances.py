'''
List files and dirs under ``/var/lib/nova/instances``
=====================================================

The parsers class in this module uses base parser class
``CommandParser`` & ``FileListing`` to list files & directories.

Parsers included in this modules are:

LsRVarLibNovaInstances - command ``ls -laR /var/lib/nova/instances``
---------------------------------------------------------------------

LsVarLibNovaInstances - command ``ls -laRZ /var/lib/nova/instances``
---------------------------------------------------------------------
'''
from insights import CommandParser, FileListing, parser
from insights.specs import Specs


@parser(Specs.ls_R_var_lib_nova_instances)
class LsRVarLibNovaInstances(CommandParser, FileListing):
    '''The class ``LsVarLibNovaInstances`` don't show file size when the
    flag `-Z` is used. This class parses the output of ``ls -laR
    /var/lib/nova/instances`` to output file listing with file size.

    Note: This issue is not seen in GNU coreutils-8.29. When the
    coreutils package is updated to 8.29 on RHEL7, this parser class
    can be deprecated.

    Typical output of the ``ls -laR /var/lib/nova/instances`` command is::

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


    Example:

        >>> ls_r_var_lib_nova_instances.dir_entry('/var/lib/nova/instances/e560e649-41fd-46a2-a3d2-5f4750ba2bb4', 'console.log')['size']
        48957
    '''
    pass


@parser(Specs.ls_var_lib_nova_instances)
class LsVarLibNovaInstances(CommandParser, FileListing):
    '''Parses the output of ``ls -laRZ /var/lib/nova/instances`` command
    which provides the SELinux directory listings of the '/var/lib/nova/instances' directory.

    The ``ls -laRZ /var/lib/nova/instances`` command provides
    information for the SELinux directory listing of the ``/var/lib/nova/instances`` directory.

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
    pass
