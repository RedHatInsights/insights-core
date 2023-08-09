import pytest

from insights.core.exceptions import ParseException
from insights.parsers.smartctl import SMARTctl
from insights.tests import context_wrap

STANDARD_DRIVE = """
smartctl 6.2 2013-07-26 r3841 [x86_64-linux-3.10.0-267.el7.x86_64] (local build)
Copyright (C) 2002-13, Bruce Allen, Christian Franke, www.smartmontools.org

=== START OF INFORMATION SECTION ===
Device Model:     ST500LM021-1KJ152
Serial Number:    W620AT02
LU WWN Device Id: 5 000c50 07817bb36
Firmware Version: 0002LIM1
User Capacity:    500,107,862,016 bytes [500 GB]
Sector Sizes:     512 bytes logical, 4096 bytes physical
Rotation Rate:    7200 rpm
Device is:        Not in smartctl database [for details use: -P showall]
ATA Version is:   ATA8-ACS T13/1699-D revision 4
SATA Version is:  SATA 3.0, 6.0 Gb/s (current: 6.0 Gb/s)
Local Time is:    Fri Sep 16 14:10:10 2016 AEST
SMART support is: Available - device has SMART capability.
SMART support is: Enabled

=== START OF READ SMART DATA SECTION ===
SMART overall-health self-assessment test result: PASSED

General SMART Values:
Offline data collection status:  (0x00) Offline data collection activity
                    was never started.
                    Auto Offline Data Collection: Disabled.
Self-test execution status:      (   0) The previous self-test routine completed
                    without error or no self-test has ever
                    been run.
Total time to complete Offline
data collection:        (    0) seconds.
Offline data collection
capabilities:            (0x73) SMART execute Offline immediate.
                    Auto Offline data collection on/off support.
                    Suspend Offline collection upon new
                    command.
                    No Offline surface scan supported.
                    Self-test supported.
                    Conveyance Self-test supported.
                    Selective Self-test supported.
SMART capabilities:            (0x0003) Saves SMART data before entering
                    power-saving mode.
                    Supports SMART auto save timer.
Error logging capability:        (0x01) Error logging supported.
                    General Purpose Logging supported.
Short self-test routine
recommended polling time:    (   1) minutes.
Extended self-test routine
recommended polling time:    (  78) minutes.
Conveyance self-test routine
recommended polling time:    (   2) minutes.
SCT capabilities:          (0x1031) SCT Status supported.
                    SCT Feature Control supported.
                    SCT Data Table supported.

SMART Attributes Data Structure revision number: 10
Vendor Specific SMART Attributes with Thresholds:
ID# ATTRIBUTE_NAME          FLAG     VALUE WORST THRESH TYPE      UPDATED  WHEN_FAILED RAW_VALUE
  1 Raw_Read_Error_Rate     0x000f   118   099   034    Pre-fail  Always       -       179599704
  3 Spin_Up_Time            0x0003   098   098   000    Pre-fail  Always       -       0
  4 Start_Stop_Count        0x0032   100   100   020    Old_age   Always       -       546
  5 Reallocated_Sector_Ct   0x0033   100   100   036    Pre-fail  Always       -       0
  7 Seek_Error_Rate         0x000f   078   060   030    Pre-fail  Always       -       61310462
  9 Power_On_Hours          0x0032   096   096   000    Old_age   Always       -       4273 (5 89 0)
 10 Spin_Retry_Count        0x0013   100   100   097    Pre-fail  Always       -       0
 12 Power_Cycle_Count       0x0032   100   100   020    Old_age   Always       -       542
184 End-to-End_Error        0x0032   100   100   099    Old_age   Always       -       0
187 Reported_Uncorrect      0x0032   100   100   000    Old_age   Always       -       0
188 Command_Timeout         0x0032   100   099   000    Old_age   Always       -       1
189 High_Fly_Writes         0x003a   100   100   000    Old_age   Always       -       0
190 Airflow_Temperature_Cel 0x0022   059   050   045    Old_age   Always       -       41 (Min/Max 21/41)
191 G-Sense_Error_Rate      0x0032   100   100   000    Old_age   Always       -       19
192 Power-Off_Retract_Count 0x0032   100   100   000    Old_age   Always       -       8
193 Load_Cycle_Count        0x0032   099   099   000    Old_age   Always       -       3009
194 Temperature_Celsius     0x0022   041   050   000    Old_age   Always       -       41 (0 11 0 0 0)
196 Reallocated_Event_Count 0x000f   096   096   030    Pre-fail  Always       -       4258 (30941 0)
197 Current_Pending_Sector  0x0012   100   100   000    Old_age   Always       -       0
198 Offline_Uncorrectable   0x0010   100   100   000    Old_age   Offline      -       0
199 UDMA_CRC_Error_Count    0x003e   200   200   000    Old_age   Always       -       0
254 Free_Fall_Sensor        0x0032   100   100   000    Old_age   Always       -       0

SMART Error Log Version: 1
No Errors Logged

SMART Self-test log structure revision number 1
Num  Test_Description    Status                  Remaining  LifeTime(hours)  LBA_of_first_error
# 1  Short offline       Completed without error       00%      2315         -

SMART Selective self-test log data structure revision number 1
 SPAN  MIN_LBA  MAX_LBA  CURRENT_TEST_STATUS
    1        0        0  Not_testing
    2        0        0  Not_testing
    3        0        0  Not_testing
    4        0        0  Not_testing
    5        0        0  Not_testing
Selective self-test flags (0x0):
  After scanning selected spans, do NOT read-scan remainder of disk.
If Selective self-test is pending on power-up, resume after 0 minute delay.

"""


def test_standard_drive():
    data = SMARTctl(context_wrap(
        STANDARD_DRIVE, path='sos_commands/ata/smartctl_-a_.dev.sda'
    ))

    # Device assertions
    assert data.device == '/dev/sda'

    # Information assertions
    assert data.information['Device Model'] == 'ST500LM021-1KJ152'
    assert data.information['Serial Number'] == 'W620AT02'
    assert data.information['LU WWN Device Id'] == '5 000c50 07817bb36'
    assert data.information['Firmware Version'] == '0002LIM1'
    assert data.information['User Capacity'] == '500,107,862,016 bytes [500 GB]'
    assert data.information['Sector Sizes'] == '512 bytes logical, 4096 bytes physical'
    assert data.information['Rotation Rate'] == '7200 rpm'
    assert data.information['Device is'] == 'Not in smartctl database [for details use: -P showall]'
    assert data.information['ATA Version is'] == 'ATA8-ACS T13/1699-D revision 4'
    assert data.information['SATA Version is'] == 'SATA 3.0, 6.0 Gb/s (current: 6.0 Gb/s)'
    assert data.information['Local Time is'] == 'Fri Sep 16 14:10:10 2016 AEST'
    # assert data.information['SMART support is'] == 'Available - device has SMART capability.'
    # Note: this key turns up twice - therefore new keys overwrite old
    assert data.information['SMART support is'] == 'Enabled'

    # Health assertions
    assert data.health == 'PASSED'

    # SMART Value assertions
    assert data.values['Offline data collection status'] == '0x00'
    assert data.values['Self-test execution status'] == '0'
    assert data.values['Total time to complete Offline data collection'] == '0'
    assert data.values['Offline data collection capabilities'] == '0x73'
    assert data.values['SMART capabilities'] == '0x0003'
    assert data.values['Error logging capability'] == '0x01'
    assert data.values['Short self-test routine recommended polling time'] == '1'
    assert data.values['Extended self-test routine recommended polling time'] == '78'
    assert data.values['Conveyance self-test routine recommended polling time'] == '2'
    assert data.values['SCT capabilities'] == '0x1031'
    assert data.values['SMART Attributes Data Structure revision number'] == '10'

    # Attribute assertions
    # Don't bother to test every single key for every single attribute - test
    # one, and then test the variations
    assert data.attributes['Raw_Read_Error_Rate']['id'] == '1'
    assert data.attributes['Raw_Read_Error_Rate']['flag'] == '0x000f'
    assert data.attributes['Raw_Read_Error_Rate']['value'] == '118'
    assert data.attributes['Raw_Read_Error_Rate']['worst'] == '099'
    assert data.attributes['Raw_Read_Error_Rate']['threshold'] == '034'
    assert data.attributes['Raw_Read_Error_Rate']['type'] == 'Pre-fail'
    assert data.attributes['Raw_Read_Error_Rate']['updated'] == 'Always'
    assert data.attributes['Raw_Read_Error_Rate']['when_failed'] == '-'
    assert data.attributes['Raw_Read_Error_Rate']['raw_value'] == '179599704'

    assert data.attributes['Start_Stop_Count']['type'] == 'Old_age'
    assert data.attributes['Power_On_Hours']['raw_value'] == '4273 (5 89 0)'
    assert data.attributes['Airflow_Temperature_Cel']['raw_value'] == '41 (Min/Max 21/41)'
    assert data.attributes['Offline_Uncorrectable']['updated'] == 'Offline'

    # No parsing leftovers
    assert not hasattr(data, 'full_line')
    # No legacy data
    assert not hasattr(data, 'info')


def test_bad_device():
    # Bad device causes a parse error
    with pytest.raises(ParseException) as exc:
        assert SMARTctl(context_wrap(
            STANDARD_DRIVE, path='sos_commands/ata/smartctl_-a'
        )) is None
    assert 'Cannot parse device name from path ' in str(exc)


CISCO_DRIVE = """
smartctl 5.43 2012-06-30 r3573 [x86_64-linux-2.6.32-573.8.1.el6.x86_64] (local build)
Copyright (C) 2002-12 by Bruce Allen, http://smartmontools.sourceforge.net

Vendor:               Cisco
Product:              UCSC-MRAID12G
Revision:             4.27
User Capacity:        898,999,779,328 bytes [898 GB]
Logical block size:   512 bytes
Logical Unit id:      0x678da6e715b756401d552c0c04e4953b
Serial number:        003b95e4040c2c551d4056b715e7a68d
Device type:          disk
Local Time is:        Wed Dec 16 21:29:59 2015 EST
Device does not support SMART

Error Counter logging not supported
Device does not support Self Test logging
"""  # noqa


def test_cisco_drive():
    data = SMARTctl(context_wrap(
        CISCO_DRIVE, path='sos_commands/ata/smartctl_-a_.dev.sdb'
    ))

    # Device assertions
    assert data.device == '/dev/sdb'

    # Information assertions
    assert data.information['Vendor'] == 'Cisco'
    assert data.information['Product'] == 'UCSC-MRAID12G'
    assert data.information['Revision'] == '4.27'
    assert data.information['User Capacity'] == '898,999,779,328 bytes [898 GB]'
    assert data.information['Logical block size'] == '512 bytes'
    assert data.information['Logical Unit id'] == '0x678da6e715b756401d552c0c04e4953b'
    assert data.information['Serial number'] == '003b95e4040c2c551d4056b715e7a68d'
    assert data.information['Device type'] == 'disk'
    assert data.information['Local Time is'] == 'Wed Dec 16 21:29:59 2015 EST'

    # Unstructured information assertions
    assert data.information['SMART support is'] == 'Not supported'
    assert data.information['Error Counter logging'] == 'Not supported'
    assert data.information['Self Test logging'] == 'Not supported'

    # Everything else is blank
    assert data.health == 'not parsed'
    assert data.values == {}
    assert data.attributes == {}


NETAPP_DRIVE = """
smartctl 5.43 2012-06-30 r3573 [x86_64-linux-2.6.32-573.8.1.el6.x86_64] (local build)
Copyright (C) 2002-12 by Bruce Allen, http://smartmontools.sourceforge.net

Vendor:               NETAPP
Product:              LUN
Revision:             820a
User Capacity:        5,243,081,326,592 bytes [5.24 TB]
Logical block size:   512 bytes
Logical Unit id:      0x60a9800044312d364d5d4478753370620x5d447875337062000a980044312d364d
Serial number:        D1-6M]Dxu3pb
Device type:          disk
Transport protocol:   iSCSI
Local Time is:        Wed Dec 16 21:29:59 2015 EST
Device supports SMART and is Enabled
Temperature Warning Disabled or Not Supported
SMART Health Status: OK

Error Counter logging not supported
Device does not support Self Test logging

"""  # noqa


def test_netapp_drive():
    data = SMARTctl(context_wrap(
        NETAPP_DRIVE, path='sos_commands/ata/smartctl_-a_.dev.sdc'
    ))

    # Device assertions
    assert data.device == '/dev/sdc'

    # Information assertions
    assert data.information['Vendor'] == 'NETAPP'
    assert data.information['Product'] == 'LUN'
    assert data.information['Revision'] == '820a'
    assert data.information['User Capacity'] == '5,243,081,326,592 bytes [5.24 TB]'
    assert data.information['Logical block size'] == '512 bytes'
    assert data.information['Logical Unit id'] == '0x60a9800044312d364d5d4478753370620x5d447875337062000a980044312d364d'
    assert data.information['Serial number'] == 'D1-6M]Dxu3pb'
    assert data.information['Device type'] == 'disk'
    assert data.information['Transport protocol'] == 'iSCSI'
    assert data.information['Local Time is'] == 'Wed Dec 16 21:29:59 2015 EST'
    assert data.information['SMART Health Status'] == 'OK'

    # Unstructured information assertions
    assert data.information['SMART support is'] == 'Enabled'
    assert data.information['Temperature Warning'] == 'Disabled or Not Supported'
    assert data.information['Error Counter logging'] == 'Not supported'
    assert data.information['Self Test logging'] == 'Not supported'

    # Everything else is blank
    assert data.health == 'not parsed'
    assert data.values == {}
    assert data.attributes == {}
