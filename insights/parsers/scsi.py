from collections import deque
from insights.core import Parser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


class Device(object):
    """
    A Device from /proc/scsi/scsi
    Sample fields:
    {
        "ansi__scsi_revision": "05",
        "vendor": "HP",
        "rev": "3.54",
        "host": "scsi0",
        "channel": "03",
        "model": "P420i",
        "type": "RAID",
        "id": "00",
        "lun": "00"
    }
    All fields are accessible as computed attributes
    """
    keys = [
        'ansi__scsi_revision',
        'vendor',
        'rev',
        'host',
        'channel',
        'model',
        'type',
        'id',
        'lun'
    ]

    def __init__(self, data):
        for k in Device.keys:
            setattr(self, k, data.get(k))

    def get(self, item, default=None):
        return self.__dict__.get(item, default)


@parser(Specs.scsi)
class SCSI(Parser):
    """
    Parses scsi info from /proc/scsi/scsi.
    Acts like an array that contains all info from scsi
    Here is some example:
    Input:
    Host: scsi0 Channel: 03 Id: 00 Lun: 00
        Vendor: HP       Model: P420i            Rev: 3.54
        Type:   RAID                             ANSI  SCSI revision: 05
    """

    HOST_KEYS = ['Host', 'Channel', 'Id', 'Lun']
    VENDOR_KEYS = ['Vendor', 'Model', 'Rev']
    TYPE_KEYS = ['Type', 'ANSI SCSI revision']
    TYPE_KEYS_ALT = ['Type', 'ANSI  SCSI revision']

    def parse_content(self, content, header='Attached devices:'):
        if not content:
            raise SkipComponent("Empty content of file /proc/scsi/scsi", content)
        devices = []
        if header:
            if content[0] != header:
                msg = 'Expected Header: %s but got %s' % (header, content[0])
                raise ParseException(msg)
            if len(content) == 1:
                raise ParseException("Content has only header but no other content: ", content)
            content = content[1:]
        lines = deque(filter(None, [line.strip() for line in content]))
        while lines:
            devices.append(self.parse_device(lines))
        self.data = devices

    """
    The TYPE line was defined in two different ways depending on RHEL version
    This method now checks for which version is used and runs collect_keys
    with the appropriate key definition
    """
    @classmethod
    def parse_device(cls, parts):
        device = {}
        cls.collect_keys(parts.popleft(), cls.HOST_KEYS, device)
        cls.collect_keys(parts.popleft(), cls.VENDOR_KEYS, device)
        type_content = parts.popleft()
        if cls.TYPE_KEYS[1] in type_content:
            cls.collect_keys(type_content, cls.TYPE_KEYS, device)
        elif cls.TYPE_KEYS_ALT[1] in type_content:
            cls.collect_keys(type_content, cls.TYPE_KEYS_ALT, device)
        return Device(device)

    @classmethod
    def collect_keys(cls, content, keys, data):
        num_keys = len(keys)
        try:
            for i, key in enumerate(keys):
                start = content.index(key)
                end = content.index(keys[i + 1]) if (i + 1) < num_keys else None
                k, v = [s.strip() for s in content[start:end].split(':')]
                data[k.lower().replace(' ', '_')] = v
        except:
            raise ParseException("Parse error for current line:", content)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for d in self.data:
            yield d

    def __getitem__(self, key):
        return self.data[key]
