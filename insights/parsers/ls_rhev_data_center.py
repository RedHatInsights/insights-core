"""
List files and dirs under ``/rhev/data-center``
===============================================

Parser included in this modules is:

LsRhevDataCenter - command ``ls -laR /rhev/data-center``
"""
from insights import CommandParser, FileListing, parser
from insights.specs import Specs


@parser(Specs.ls_rhev_data_center)
class LsRhevDataCenter(CommandParser, FileListing):
    """Parse the output of ``ls -laR /rhev/data-center`` command. It uses the base
    parser class ``CommandParser`` & ``FileListing`` to list files & directories.

    Typical output of the ``ls -laR /rhev/data-center`` command is::

        /rhev/data-center:
        total 0
        drwxr-xr-x. 2 vdsm kvm 154 Aug 21 20:18 16b94b39-7229-481e-914d-c827e2ad2071
        drwxr-xr-x. 6 vdsm kvm 152 May 29  2018 mnt

        /rhev/data-center/16b94b39-7229-481e-914d-c827e2ad2071:
        total 0
        lrwxrwxrwx. 1 vdsm kvm 95 May 22  2018 a384bf5d-db92-421e-926d-bfb99a6b4b28 -> /rhev/data-center/mnt/host1.example.com:_nfsshare_data/a384bf5d-db92-421e-926d-bfb99a6b4b28

        /rhev/data-center/mnt:
        total 12
        drwxrwxr-x. 3 vdsm kvm 4096 Nov 17  2015 host1.example.com:_nfsshare_data

        /rhev/data-center/mnt/host1.example.com:_nfsshare_data:
        total 4
        drwxr-xr-x. 4 vdsm kvm 4096 Nov 17  2015 a384bf5d-db92-421e-926d-bfb99a6b4b28

        /rhev/data-center/mnt/host1.example.com:_nfsshare_data/a384bf5d-db92-421e-926d-bfb99a6b4b28:
        total 16
        drwxr-xr-x. 89 vdsm kvm 12288 Dec 19 15:02 images

        /rhev/data-center/mnt/host1.example.com:_nfsshare_data/a384bf5d-db92-421e-926d-bfb99a6b4b28/images:
        total 348
        drwxr-xr-x. 2 vdsm kvm 4096 Feb 26  2018 b7d6cc07-d1f1-44b3-b3c0-7067ec7056a3

        /rhev/data-center/mnt/host1.example.com:_nfsshare_data/a384bf5d-db92-421e-926d-bfb99a6b4b28/images/b7d6cc07-d1f1-44b3-b3c0-7067ec7056a3:
        total 12131848
        -rw-rw----. 1 root root 32212254720 Dec 19 14:06 4d6e5dea-995f-4a4e-b487-0f70361f6137
        -rw-rw----. 1 vdsm kvm      1048576 Feb 26  2018 4d6e5dea-995f-4a4e-b487-0f70361f6137.lease
        -rw-r--r--. 1 vdsm kvm          269 Feb 26  2018 4d6e5dea-995f-4a4e-b487-0f70361f6137.meta

    Example:

        >>> ls_rhev_dc.dir_entry('/rhev/data-center/mnt/host1.example.com:_nfsshare_data/a384bf5d-db92-421e-926d-bfb99a6b4b28/images/b7d6cc07-d1f1-44b3-b3c0-7067ec7056a3', '4d6e5dea-995f-4a4e-b487-0f70361f6137')['owner']
        'root'
        >>> ls_rhev_dc.dir_entry('/rhev/data-center/mnt/host1.example.com:_nfsshare_data/a384bf5d-db92-421e-926d-bfb99a6b4b28/images/b7d6cc07-d1f1-44b3-b3c0-7067ec7056a3', '4d6e5dea-995f-4a4e-b487-0f70361f6137')['group']
        'root'
    """
    pass
