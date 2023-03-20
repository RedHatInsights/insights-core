import pytest

from insights.core.exceptions import ParseException
from insights.parsers.systool import SystoolSCSIBus
from insights.tests import context_wrap

SYSTOOL_B_SCSI_V_1 = """
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
  Device path = "/sys/devices/pci0000:00/0000:00:0d.0/ata3/host2/target2:0:0/2:0:0:0"
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
    iodone_cnt          = "0x208c"
    ioerr_cnt           = "0x2"
    iorequest_cnt       = "0x20a6"
    modalias            = "scsi:t-0x00"
    model               = "VBOX HARDDISK   "
    queue_depth         = "31"
    queue_ramp_up_period= "120000"
    queue_type          = "simple"
    rescan              = <store method only>
    rev                 = "1.0 "
    scsi_level          = "6"
    state               = "running"
    timeout             = "30"
    type                = "0"
    uevent              = "DEVTYPE=scsi_device
DRIVER=sd
MODALIAS=scsi:t-0x00"
    unpriv_sgio         = "0"
    vendor              = "ATA     "
    vpd_pg80            =
    vpd_pg83            =

  Device = "host0"
  Device path = "/sys/devices/pci0000:00/0000:00:01.1/ata1/host0"
    uevent              = "DEVTYPE=scsi_host"

  Device = "host1"
  Device path = "/sys/devices/pci0000:00/0000:00:01.1/ata2/host1"
    uevent              = "DEVTYPE=scsi_host"

  Device = "host2"
  Device path = "/sys/devices/pci0000:00/0000:00:0d.0/ata3/host2"
    uevent              = "DEVTYPE=scsi_host"

  Device = "target1:0:0"
  Device path = "/sys/devices/pci0000:00/0000:00:01.1/ata2/host1/target1:0:0"
    uevent              = "DEVTYPE=scsi_target"

  Device = "target2:0:0"
  Device path = "/sys/devices/pci0000:00/0000:00:0d.0/ata3/host2/target2:0:0"
    uevent              = "DEVTYPE=scsi_target"

"""

SYSTOOL_B_SCSI_V_ILLEGAL_2 = """
Bus = "scsi"

  Device = "1:0:0:0"
  Device path = "/sys/devices/pci0000:00/0000:00:01.1/ata2/host1/target1:0:0/1:0:0:0"
    delete              = <store method only>
    type                is "5"
    uevent              = "DEVTYPE=scsi_device
DRIVER=sr
MODALIAS=scsi:t-0x05"
    unpriv_sgio         = "0"
    vendor              = "VBOX    "
"""

SYSTOOL_B_SCSI_V_ILLEGAL_3 = """
Bus = "scsi"

  Device = "1:0:0:0"
  Device path = "/sys/devices/pci0000:00/0000:00:01.1/ata2/host1/target1:0:0/1:0:0:0"
    delete              = <store method only>
                        = "5"
    uevent              = "DEVTYPE=scsi_device
DRIVER=sr
MODALIAS=scsi:t-0x05"
    unpriv_sgio         = "0"
    vendor              = "VBOX    "
"""

SYSTOOL_B_SCSI_V_ILLEGAL_4 = """
Bus = "scsi"

  Device path = "/sys/devices/pci0000:00/0000:00:01.1/ata2/host1/target1:0:0/1:0:0:0"
    delete              = <store method only>
    type                = "5"
    uevent              = "DEVTYPE=scsi_device
DRIVER=sr
MODALIAS=scsi:t-0x05"
    unpriv_sgio         = "0"
    vendor              = "VBOX    "
"""

SYSTOOL_B_SCSI_V_ILLEGAL_5 = """
Bus = "scsi"

"""

SYSTOOL_B_SCSI_V_ILLEGAL_6 = """
Bus = "abc"

"""


def test_systoolscsibus_with_legal_input():
    res = SystoolSCSIBus(context_wrap(SYSTOOL_B_SCSI_V_1))

    assert len(res.data) == 7
    assert len(res.devices[0]) == 30
    assert len(res.devices[1]) == 33
    assert res.data['1:0:0:0']['uevent'] == 'DEVTYPE=scsi_device DRIVER=sr MODALIAS=scsi:t-0x05'
    assert res.data['1:0:0:0']['delete'] == '<store method only>'
    assert res.devices[1].get('vpd_pg83') == ''
    assert res.devices[1].get('not_exist') is None

    assert all([d.get('Device path') for d in res.devices])

    assert res.get_device_state('2:0:0:0') == 'running'
    assert res.get_device_state('host2') is None
    assert res.get_device_state('host_what') is None


def test_systoolscsibus_with_illegal_input():
    with pytest.raises(ParseException) as e_info:
        SystoolSCSIBus(context_wrap(SYSTOOL_B_SCSI_V_ILLEGAL_2))
    assert "Unparseable line without = " in str(e_info.value)

    with pytest.raises(ParseException) as e_info:
        SystoolSCSIBus(context_wrap(SYSTOOL_B_SCSI_V_ILLEGAL_3))
    assert "Unparseable line without key" in str(e_info.value)

    with pytest.raises(ParseException) as e_info:
        SystoolSCSIBus(context_wrap(SYSTOOL_B_SCSI_V_ILLEGAL_4))
    assert "Parsing Error for no heading Device-name" in str(e_info.value)

    with pytest.raises(ParseException) as e_info:
        SystoolSCSIBus(context_wrap(SYSTOOL_B_SCSI_V_ILLEGAL_5))
    assert "Parsing Error for this almost empty input." in str(e_info.value)

    with pytest.raises(ParseException) as e_info:
        SystoolSCSIBus(context_wrap(SYSTOOL_B_SCSI_V_ILLEGAL_6))
    assert "Unparseable first line of input:" in str(e_info.value)
