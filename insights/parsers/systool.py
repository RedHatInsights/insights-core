"""
Command ``systool`` outputs - Commands
======================================

Command systool uses APIs provided by libsysfs to gather information.

Parser included in this module is:

SystoolSCSIBus - command ``/bin/systool -b scsi -v``
----------------------------------------------------

"""

from . import ParseException
from .. import LegacyItemAccess, CommandParser, parser
from ..specs import Specs


@parser(Specs.systool_b_scsi_v)
class SystoolSCSIBus(LegacyItemAccess, CommandParser):
    """
    Class for parsing ``/bin/systool -b scsi -v`` command output

    Typical command output::

        Bus = "scsi"

          Device = "1:0:0:0"
          Device path = "/sys/devices/pci0000:00/0000:00:01.1/ata2/host1/target1:0:0/1:0:0:0"
            delete              = <store method only>
            device_blocked      = "0"
            device_busy         = "0"
            dh_state            = "detached"
            eh_timeout          = "10"
            evt_capacity_change_reported= "0"
            evt_inquiry_change_reported= "0"
            evt_lun_change_reported= "0"
            evt_media_change    = "0"
            evt_mode_parameter_change_reported= "0"
            evt_soft_threshold_reached= "0"
            iocounterbits       = "32"
            iodone_cnt          = "0x15b"
            ioerr_cnt           = "0x3"
            iorequest_cnt       = "0x16c"
            modalias            = "scsi:t-0x05"
            model               = "CD-ROM          "
            queue_depth         = "1"
            queue_type          = "none"
            rescan              = <store method only>
            rev                 = "1.0 "
            scsi_level          = "6"
            state               = "running"
            timeout             = "30"
            type                = "5"
            uevent              = "DEVTYPE=scsi_device
        DRIVER=sr
        MODALIAS=scsi:t-0x05"
            unpriv_sgio         = "0"
            vendor              = "VBOX    "

          Device = "2:0:0:0"
          ...

    Examples:
        >>> len(res.data)
        2
        >>> res.data.keys()
        ['1:0:0:0', '2:0:0:0']
        >>> res.device_names
        ['1:0:0:0', '2:0:0:0']
        >>> res.data['1:0:0:0'] == res.devices[0]
        True
        >>> res.get_device_state('1:0:0:0')
        'running'
        >>> res.get_device_state('2:0:0:0')
        None

    """

    def parse_content(self, content):

        content = [l for l in content if l]

        if content[0] and not all([v in content[0] for v in ("Bus", "=", "scsi")]):
            raise ParseException("Unparseable first line of input: %s" % content[0])

        if len(content) <= 2:
            raise ParseException("Parsing Error for this almost empty input.")

        self.devices = []
        self.device_names = []
        multi_lines_str = None

        for _l in content[1:]:
            l = _l.strip()
            if not multi_lines_str:
                # Starter of a new logical line
                k, v = self._split_line(l)
                if v.startswith('"') and not v.endswith('"'):
                    # Starter of a multi_lines line
                    multi_lines_str = l + ' '
                else:
                    # fairly a normal line
                    self._record_pair(k, v)
            else:
                # Continue that multi-lines line
                if l.endswith('"'):
                    # End of a multi_lines line
                    multi_lines_str += l
                    k, v = self._split_line(multi_lines_str)
                    multi_lines_str = None
                    self._record_pair(k, v)
                else:
                    # Mid of a multi_lines line
                    multi_lines_str += l + ' '

        data = {}
        for k, v in zip(self.device_names, self.devices):
            data[k] = v
        self.data = data

    def _split_line(self, line):
        if '=' not in line:
            raise ParseException("Unparseable line without = : %s", line)
        _k, _v = line.split('=', 1)
        k = _k.strip()
        v = _v.strip()
        if not k:
            raise ParseException("Unparseable line without key : %s" % line)
        return k, v

    def _record_pair(self, k, _v):
        v = _v.strip(' "')
        if k == 'Device':
            self.device_names.append(v)
            self.devices.append({k: v})
        else:
            try:
                self.devices[-1][k] = v
            except IndexError:
                raise ParseException("Parsing Error for no heading Device-name \
                                      of (key, value) pair: (%s, %s)" % (k, v))

    def get_device_state(self, device_name):
        """
        Return the state value of the given device_name.
        Return None for unexist device_name or no state value.
        """
        device_info = self.data.get(device_name)
        return device_info.get('state') if device_info else None
