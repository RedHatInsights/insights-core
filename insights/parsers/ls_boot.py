"""
LsBoot - command ``ls -lanR /boot``
===================================

The ``ls -lanR /boot`` command provides information for the listing of the
``/boot`` directory.

See the ``FileListing`` class for a more complete description of the
available features of the class.

Sample directory listing::

    /boot:
    total 187380
    dr-xr-xr-x.  3 0 0     4096 Mar  4 16:19 .
    dr-xr-xr-x. 19 0 0     4096 Jul 14 09:10 ..
    -rw-r--r--.  1 0 0   123891 Aug 25  2015 config-3.10.0-229.14.1.el7.x86_64

    /boot/grub2:
    total 36
    drwxr-xr-x. 6 0 0  104 Mar  4 16:16 .
    dr-xr-xr-x. 3 0 0 4096 Mar  4 16:19 ..
    lrwxrwxrwx. 1 0 0     11 Aug  4  2014 menu.lst -> ./grub.conf
    -rw-r--r--. 1 0 0   64 Sep 18  2015 device.map

Examples:

    >>> bootdir = shared[LsBoot]
    >>> '/boot' in bootdir
    True
    >>> '/boot/grub' in bootdir
    False
    >>> bootdir.files_of('/boot')
    ['config-3.10.0-229.14.1.el7.x86_64']
    >>> bootdir.dir_contains('/boot/grub2', 'menu.lst')
    True
"""

from .. import FileListing, parser


@parser("ls_boot")
class LsBoot(FileListing):
    """
    Parse the /boot directory listing using a standard FileListing parser.

    We also provide a ``data`` property that lists all the files found in
    the boot directory, for compatibility with certain older plugins.
    """

    def parse_content(self, content):
        """
        Parse the directory content.

        One usage example requires a 'data' property for these operations::

            missing_kernels = [k for k in grub_kernels if k not in boot_files]
            missing_initrds = [i for i in grub_initrds if i not in boot_files]

        So the ``data`` property is set to be a list of the files in all
        found directories to satisfy this plugin.  Do not rely on this as it
        will be deprecated in the future.
        """
        super(LsBoot, self).parse_content(content)
        # Data attribute for missing_boot_files: all files found in all
        # directories, in one list.
        self.data = []
        for direct in self.listings.values():
            self.data.extend(direct['files'])
