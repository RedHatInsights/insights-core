from falafel.core.plugins import mapper
from falafel.core import MapperOutput
from falafel.mappers import get_active_lines


@mapper("ls_disk")
class LsDisk(MapperOutput):

    @staticmethod
    def parse_content(content):
        """
            parsing ls_disk and return all the link files in a dict.
            Input Example:
                /dev/disk/by-id:
                total 0
                drwxr-xr-x. 2 0 0 360 Sep 20 09:36 .
                drwxr-xr-x. 5 0 0 100 Sep 20 09:36 ..
                lrwxrwxrwx. 1 0 0   9 Sep 20 09:36 ata-VBOX_CD-ROM_VB2-01700376 -> ../../sr0
                lrwxrwxrwx. 1 0 0   9 Sep 20 09:36 ata-VBOX_HARDDISK_VB4c56cb04-26932e6a -> ../../sdb
                lrwxrwxrwx. 1 0 0  10 Sep 20 09:36 ata-VBOX_HARDDISK_VB4c56cb04-26932e6a-part1 -> ../../sdb1
                lrwxrwxrwx. 1 0 0  10 Sep 20 09:36 scsi-SATA_VBOX_HARDDISK_VB4c56cb04-26932e6a-part1 -> ../../sdb1

                /dev/disk/by-path:
                total 0
                drwxr-xr-x. 2 0 0 160 Sep 20 09:36 .
                drwxr-xr-x. 5 0 0 100 Sep 20 09:36 ..
                lrwxrwxrwx. 1 0 0   9 Sep 20 09:36 pci-0000:00:0d.0-scsi-1:0:0:0 -> ../../sdb
                lrwxrwxrwx. 1 0 0  10 Sep 20 09:36 pci-0000:00:0d.0-scsi-1:0:0:0-part1 -> ../../sdb1

                /dev/disk/by-uuid:
                total 0
                drwxr-xr-x. 2 0 0 100 Sep 20 09:36 .
                drwxr-xr-x. 5 0 0 100 Sep 20 09:36 ..
                lrwxrwxrwx. 1 0 0  10 Sep 20 09:36 3ab50b34-d0b9-4518-9f21-05307d895f81 -> ../../dm-1
                lrwxrwxrwx. 1 0 0  10 Sep 20 09:36 51c5cf12-a577-441e-89da-bc93a73a1ba3 -> ../../sda1
                lrwxrwxrwx. 1 0 0  10 Sep 20 09:36 7b0068d4-1399-4ce7-a54a-3e2fc1232299 -> ../../dm-0
            Output Example:
                {'/dev/disk/by-uuid': {'sda1': ['51c5cf12-a577-441e-89da-bc93a73a1ba3'], 'dm-0': ['7b0068d4-1399-4ce7-a54a-3e2fc1232299']...}
                '/dev/disk/by-path': {'sr0': ['pci-0000:00:01.1-scsi-1:0:0:0']...}
                '/dev/disk/by-id' : {'sdb1': ['ata-VBOX_HARDDISK_VB4c56cb04-26932e6a-part1','scsi-SATA_VBOX_HARDDISK_VB4c56cb04-26932e6a-part1']}
                ...}
        """

        dir_dict = {}
        section_dict = {}
        for line in get_active_lines(content):
            if line.startswith('/dev/disk'):
                section_dict = {}
                dir_dict[line.strip(':')] = section_dict
            elif line.startswith('l'):
                section_dict.setdefault(line.split()[-1].split('/')[-1], []).append(line.split()[-3])
        return dir_dict
