from insights.parsers.dmidecode import DMIDecode
from insights.tests import context_wrap

from datetime import date

DMIDECODE = '''
# dmidecode 2.11
SMBIOS 2.7 present.
188 structures occupying 5463 bytes.
Table at 0xBFFCB000.

Handle 0x0000, DMI type 0, 24 bytes
BIOS Information
\tVendor: HP
\tVersion: P70
\tRelease Date: 03/01/2013
\tAddress: 0xF0000
\tRuntime Size: 64 kB
\tROM Size: 8192 kB
\tCharacteristics:
\t\tPCI is supported
\t\tPNP is supported
\t\tBIOS is upgradeable
\t\tBIOS shadowing is allowed
\t\tESCD support is available
\t\tBoot from CD is supported
\t\tSelectable boot is supported
\t\tEDD is supported
\t\t5.25"/360 kB floppy services are supported (int 13h)
\t\t5.25"/1.2 MB floppy services are supported (int 13h)
\t\t3.5"/720 kB floppy services are supported (int 13h)
\t\tPrint screen service is supported (int 5h)
\t\tj042 keyboard services are supported (int 9h)
\t\tSerial services are supported (int 14h)
\t\tPrinter services are supported (int 17h)
\t\tCGA/mono video services are supported (int 10h)
\t\tACPI is supported
\t\tUSB legacy is supported
\t\tBIOS boot specification is supported
\t\tFunction key-initiated network boot is supported
\t\tTargeted content distribution is supported
\tFirmware Revision: 1.22

Handle 0x0100, DMI type 1, 27 bytes
System Information
\tManufacturer: HP
\tProduct Name: ProLiant DL380p Gen8
\tVersion: Not Specified
\tSerial Number: 2M23360006
\tUUID: 34373936-3439-4D32-3233-333630303036
\tWake-up Type: Power Switch
\tSKU Number: 697494-S01
\tFamily: ProLiant

Handle 0x0300, DMI type 3, 21 bytes
chassis information
\tmanufacturer: hp
\ttype: rack mount chassis
\tlock: not present
\tversion: not specified
\tserial number: 2m23360006
\tasset Tag:
\tBoot-up State: Safe
\tPower Supply State: Safe
\tThermal State: Safe
\tSecurity Status: Unknown
\tOEM Information: 0x00000000
\tHeight: 2 U
\tNumber Of Power Cords: 2
\tContained Elements: 0

Handle 0x0401, DMI type 4, 32 bytes
Processor Information
\tSocket Designation: CPU 1
\tType: Central Processor
\tFamily: Other
\tManufacturer: Bochs
\tID: A1 06 02 00 FD FB 8B 17
\tVersion: Not Specified
\tVoltage: Unknown
\tExternal Clock: Unknown
\tMax Speed: 2000 MHz
\tCurrent Speed: 2000 MHz
\tStatus: Populated, Enabled
\tUpgrade: Other
\tL1 Cache Handle: Not Provided
\tL2 Cache Handle: Not Provided
\tL3 Cache Handle: Not Provided

Handle 0x0402, DMI type 4, 32 bytes
Processor Information
\tSocket Designation: CPU 2
\tType: Central Processor
\tFamily: Other
\tManufacturer: Bochs
\tID: A1 06 02 00 FD FB 8B 17
\tVersion: Not Specified
\tVoltage: Unknown
\tExternal Clock: Unknown
\tMax Speed: 2000 MHz
\tCurrent Speed: 2000 MHz
\tStatus: Populated, Enabled
\tUpgrade: Other
\tL1 Cache Handle: Not Provided
\tL2 Cache Handle: Not Provided
\tL3 Cache Handle: Not Provided

Handle 0x0037, DMI type 127, 4 bytes.
End Of Table
'''

DMIDECODE_V = '''
# dmidecode 2.12
SMBIOS 2.4 present.
364 structures occupying 16870 bytes.
Table at 0x000E0010.

Handle 0x0000, DMI type 0, 24 bytes
BIOS Information
\tVendor: Phoenix Technologies LTD
\tVersion: 6.00
\tRelease Date: 04/14/2014
\tAddress: 0xEA050
\tRuntime Size: 90032 bytes
\tROM Size: 64 kB
\tCharacteristics:
\t\tISA is supported
\t\tPCI is supported
\t\tPC Card (PCMCIA) is supported
\t\tPNP is supported
\t\tAPM is supported
\t\tBIOS is upgradeable
\t\tBIOS shadowing is allowed
\t\tESCD support is available
\t\tBoot from CD is supported
\t\tSelectable boot is supported
\t\tEDD is supported
\t\tPrint screen service is supported (int 5h)
\t\t8042 keyboard services are supported (int 9h)
\t\tSerial services are supported (int 14h)
\t\tPrinter services are supported (int 17h)
\t\tCGA/mono video services are supported (int 10h)
\t\tACPI is supported
\t\tSmart battery is supported
\t\tBIOS boot specification is supported
\t\tFunction key-initiated network boot is supported
\t\tTargeted content distribution is supported
\tBIOS Revision: 4.6
\tFirmware Revision: 0.0

Handle 0x0001, DMI type 1, 27 bytes
System Information
\tManufacturer: VMware, Inc.
\tProduct Name: VMware Virtual Platform
\tVersion: None
\tSerial Number: VMware-42 10 e9 13 1e 11 e2 21-13 c5 c8 1f 11 42 7c cb
\tUUID: 4210E913-1E11-E221-13C5-C81F11427CCB
\tWake-up Type: Power Switch
\tSKU Number: Not Specified
\tFamily: Not Specified
'''

DMIDECODE_AWS = '''
# dmidecode 2.12-dmifs
SMBIOS 2.4 present.
11 structures occupying 310 bytes.
Table at 0x000EB01F.

Handle 0x0000, DMI type 0, 24 bytes
BIOS Information
\tVendor: Xen
\tVersion: 4.2.amazon
\tRelease Date: 12/09/2016
\tAddress: 0xE8000
\tRuntime Size: 96 kB
\tROM Size: 64 kB
\tCharacteristics:
\t\tPCI is supported
\t\tEDD is supported
\t\tTargeted content distribution is supported
\tBIOS Revision: 4.2

Handle 0x0100, DMI type 1, 27 bytes
System Information
\tManufacturer: Xen
\tProduct Name: HVM domU
\tVersion: 4.2.amazon
\tSerial Number: ec2f58af-2dad-c57e-88c0-a81cb6084290
\tUUID: EC2F58AF-2DAD-C57E-88C0-A81CB6084290
\tWake-up Type: Power Switch
\tSKU Number: Not Specified
\tFamily: Not Specified

Handle 0x0300, DMI type 3, 13 bytes
Chassis Information
\tManufacturer: Xen
\tType: Other
\tLock: Not Present
\tVersion: Not Specified
\tSerial Number: Not Specified
\tAsset Tag: Not Specified
\tBoot-up State: Safe
\tPower Supply State: Safe
\tThermal State: Safe
\tSecurity Status: Unknown
'''

DMIDECODE_KVM = '''
# dmidecode 3.0
Scanning /dev/mem for entry point.
SMBIOS 2.8 present.
13 structures occupying 788 bytes.
Table at 0xBFFFFCE0.

Handle 0x0000, DMI type 0, 24 bytes
BIOS Information
\tVendor: SeaBIOS
\tVersion: 1.9.1-5.el7_3.2
\tRelease Date: 04/01/2014
\tAddress: 0xE8000
\tRuntime Size: 96 kB
\tROM Size: 64 kB
\tCharacteristics:
\t\tBIOS characteristics not supported
\t\tTargeted content distribution is supported
\tBIOS Revision: 0.0

Handle 0x0100, DMI type 1, 27 bytes
System Information
\tManufacturer: Red Hat
\tProduct Name: RHEV Hypervisor
\tVersion: 7.3-7.el7
\tSerial Number: 34353737-3035-4E43-3734-353130425732
\tUUID: 10331906-BB22-4716-8876-3DFEF8FA941E
\tWake-up Type: Power Switch
\tSKU Number: Not Specified
\tFamily: Red Hat Enterprise Linux

Handle 0x0300, DMI type 3, 21 bytes
Chassis Information
\tManufacturer: Red Hat
\tType: Other
\tLock: Not Present
\tVersion: RHEL 7.2.0 PC (i440FX + PIIX, 1996)
\tSerial Number: Not Specified
\tAsset Tag: Not Specified
\tBoot-up State: Safe
\tPower Supply State: Safe
\tThermal State: Safe
\tSecurity Status: Unknown
\tOEM Information: 0x00000000
\tHeight: Unspecified
\tNumber Of Power Cords: Unspecified
\tContained Elements: 0
'''

DMIDECODE_FAIL = "# dmidecode 2.11\n# No SMBIOS nor DMI entry point found, sorry.\n"

DMIDECODE_DMI = '''
# dmidecode 2.2
SMBIOS 2.4 present.
104 structures occupying 3162 bytes.
Table at 0x000EE000.
Handle 0x0000
\tDMI type 0, 24 bytes.
\tBIOS Information
\t\tVendor: HP
\t\tVersion: A08
\t\tRelease Date: 09/27/2008
\t\tAddress: 0xF0000
\t\tRuntime Size: 64 kB
\t\tROM Size: 4096 kB
\t\tCharacteristics:
\t\t\tPCI is supported
\t\t\tPNP is supported
\t\t\tBIOS is upgradeable
\t\t\tBIOS shadowing is allowed
\t\t\tESCD support is available
\t\t\tBoot from CD is supported
\t\t\tSelectable boot is supported
\t\t\tEDD is supported
\t\t\t5.25"/360 KB floppy services are supported (int 13h)
\t\t\t5.25"/1.2 MB floppy services are supported (int 13h)
\t\t\t3.5"/720 KB floppy services are supported (int 13h)
\t\t\tPrint screen service is supported (int 5h)
\t\t\t8042 keyboard services are supported (int 9h)
\t\t\tSerial services are supported (int 14h)
\t\t\tPrinter services are supported (int 17h)
\t\t\tCGA/mono video services are supported (int 10h)
\t\t\tACPI is supported
\t\t\tUSB legacy is supported
\t\t\tBIOS boot specification is supported
\t\t\tFunction key-initiated network boot is supported``
Handle 0x0100
\tDMI type 1, 27 bytes.
\tSystem Information
\t\tManufacturer: HP
\t\tProduct Name: ProLiant BL685c G1
\t\tVersion: Not Specified
\t\tSerial Number: 3H6CMK2537
\t\tUUID: 58585858-5858-3348-3643-4D4B32353337
\t\tWake-up Type: Power Switch
'''

# Several oddities in processing that should be picked up:
# * Things besides 'Characteristics' that are double-indented
# * Multiple instances of the same heading
# * A subheading with a value on that line and subsequent double-indented data.
DMIDECODE_ODDITIES = """
Handle 0x0009, DMI type 129, 8 bytes
OEM-specific Type
\tHeader and Data:
\t\t81 08 09 00 01 01 02 01
\tStrings:
\t\tIntel_ASF
\t\tIntel_ASF_001

Handle 0x000A, DMI type 134, 13 bytes
OEM-specific Type
\tHeader and Data:
\t\t86 0D 0A 00 28 06 14 20 00 00 00 00 00

Handle 0x000F, DMI type 8, 9 bytes
Port Connector Information
\tInternal Reference Designator: Not Available
\tInternal Connector Type: None
\tExternal Reference Designator: USB 1
\tExternal Connector Type: Access Bus (USB)
\tPort Type: USB

Handle 0x0010, DMI type 8, 9 bytes
Port Connector Information
\tInternal Reference Designator: Not Available
\tInternal Connector Type: None
\tExternal Reference Designator: USB 2
\tExternal Connector Type: Access Bus (USB)
\tPort Type: USB

Handle 0x0029, DMI type 13, 22 bytes
BIOS Language Information
\tLanguage Description Format: Abbreviated
\tInstallable Languages: 1
\t\ten-US
\tCurrently Installed Language: en-US

Handle 0x000A, DMI type 134, 13 bytes
OEM-specific Type
\tHeader and Data:
\t\t01 02 03 04 05 06 07 08

"""


def test_get_dmidecode():
    '''
    Test for three kinds of output format of dmidecode parser
    '''
    context = context_wrap(DMIDECODE)
    ret = DMIDecode(context)

    assert len(ret.get("bios_information")) == 1
    assert ret.get("bios_information")[0].get("vendor") == "HP"
    assert ret.get("bios_information")[0].get("version") == "P70"
    assert ret.get("bios_information")[0].get("release_date") == "03/01/2013"
    assert ret.get("bios_information")[0].get("address") == "0xF0000"
    assert ret.get("bios_information")[0].get("runtime_size") == "64 kB"
    assert ret.get("bios_information")[0].get("rom_size") == "8192 kB"

    tmp = ["PCI is supported", "PNP is supported", "BIOS is upgradeable",
           "BIOS shadowing is allowed", "ESCD support is available",
           "Boot from CD is supported", "Selectable boot is supported",
           "EDD is supported",
           '5.25"/360 kB floppy services are supported (int 13h)',
           '5.25"/1.2 MB floppy services are supported (int 13h)',
           '3.5"/720 kB floppy services are supported (int 13h)',
           "Print screen service is supported (int 5h)",
           "j042 keyboard services are supported (int 9h)",
           "Serial services are supported (int 14h)",
           "Printer services are supported (int 17h)",
           "CGA/mono video services are supported (int 10h)",
           "ACPI is supported", "USB legacy is supported",
           "BIOS boot specification is supported",
           "Function key-initiated network boot is supported",
           "Targeted content distribution is supported"]
    assert ret.get("bios_information")[0].get("characteristics") == tmp
    assert ret.get("bios_information")[0].get("firmware_revision") == "1.22"

    assert len(ret.get("system_information")) == 1
    assert ret.get("system_information")[0].get("manufacturer") == "HP"
    assert ret.get("system_information")[0].get("product_name") == "ProLiant DL380p Gen8"
    assert ret.get("system_information")[0].get("version") == "Not Specified"
    assert ret.get("system_information")[0].get("serial_number") == "2M23360006"
    assert ret.get("system_information")[0].get("uuid") == "34373936-3439-4D32-3233-333630303036"
    assert ret.get("system_information")[0].get("wake-up_type") == "Power Switch"
    assert ret.get("system_information")[0].get("sku_number") == "697494-S01"
    assert ret.get("system_information")[0].get("family") == "ProLiant"

    assert len(ret.get("chassis_information")) == 1
    assert ret.get("chassis_information")[0].get("manufacturer") == "hp"
    assert ret.get("chassis_information")[0].get("type") == "rack mount chassis"
    assert ret.get("chassis_information")[0].get("lock") == "not present"
    assert ret.get("chassis_information")[0].get("version") == "not specified"
    assert ret.get("chassis_information")[0].get("serial_number") == "2m23360006"
    assert ret.get("chassis_information")[0].get("asset_tag") == ""
    assert ret.get("chassis_information")[0].get("boot-up_state") == "Safe"
    assert ret.get("chassis_information")[0].get("power_supply_state") == "Safe"
    assert ret.get("chassis_information")[0].get("thermal_state") == "Safe"
    assert ret.get("chassis_information")[0].get("security_status") == "Unknown"
    assert ret.get("chassis_information")[0].get("oem_information") == "0x00000000"
    assert ret.get("chassis_information")[0].get("height") == "2 U"
    assert ret.get("chassis_information")[0].get("number_of_power_cords") == "2"
    assert ret.get("chassis_information")[0].get("manufacturer") == "hp"
    assert ret.get("chassis_information")[0].get("contained_elements") == "0"

    assert len(ret.get('processor_information')) == 2
    assert ret.get("processor_information")[0].get("socket_designation") == "CPU 1"
    assert ret.get("processor_information")[0].get("type") == "Central Processor"

    assert ret.get("processor_information")[1].get("socket_designation") == "CPU 2"
    assert ret.get("processor_information")[1].get("type") == "Central Processor"

    # Check for 'nonsense' keys
    assert 'table_at_0xbffcb000.' not in ret

    # Test property accessors
    assert ret.system_info == ret['system_information'][0]
    assert ret.system_uuid == '34373936-3439-4D32-3233-333630303036'.lower()
    assert ret.bios == ret['bios_information'][0]
    assert ret.bios_vendor == 'HP'
    assert ret.bios_date == date(2013, 3, 1)
    assert ret.processor_manufacturer == 'Bochs'


def test_get_dmidecode_fail():
    '''
    Test for faied raw data
    '''
    context = context_wrap(DMIDECODE_FAIL)
    ret = DMIDecode(context)

    assert ret.is_present is False
    assert ret.system_uuid is None


# def test_virt_what_1():
#     '''
#     Test for virt_what()
#     '''
#     context = context_wrap(DMIDECODE_V)
#     ret = DMIDecode(context)
#     assert ret.is_present is True
#     assert ret.virt_what == "vmware"


# def test_virt_what_2():
#     '''
#     Test for virt_what() with AWS data
#     '''
#     context = context_wrap(DMIDECODE_AWS)
#     ret = DMIDecode(context)
#     assert ret.is_present is True
#     assert ret.virt_what == "amazon"


# def test_virt_what_3():
#     '''
#     Test for virt_what() with KVM
#     '''
#     context = context_wrap(DMIDECODE_KVM)
#     ret = DMIDecode(context)
#     assert ret.is_present is True
#     assert ret.virt_what == "kvm"


def test_get_dmidecode_dmi():
    '''
    Test for three kinds of output format of dmidecode parser
    with special input format:
    "\n\tDMI" in the input
    '''
    context = context_wrap(DMIDECODE_DMI)
    ret = DMIDecode(context)

    assert ret.get("bios_information")[0].get("vendor") == "HP"
    assert ret.get("bios_information")[0].get("version") == "A08"
    assert ret.get("bios_information")[0].get("release_date") == "09/27/2008"
    assert ret.get("bios_information")[0].get("address") == "0xF0000"
    assert ret.get("bios_information")[0].get("runtime_size") == "64 kB"
    assert ret.get("bios_information")[0].get("rom_size") == "4096 kB"

    tmp = ["PCI is supported", "PNP is supported", "BIOS is upgradeable",
           "BIOS shadowing is allowed", "ESCD support is available",
           "Boot from CD is supported", "Selectable boot is supported",
           "EDD is supported",
           '5.25"/360 KB floppy services are supported (int 13h)',
           '5.25"/1.2 MB floppy services are supported (int 13h)',
           '3.5"/720 KB floppy services are supported (int 13h)',
           "Print screen service is supported (int 5h)",
           "8042 keyboard services are supported (int 9h)",
           "Serial services are supported (int 14h)",
           "Printer services are supported (int 17h)",
           "CGA/mono video services are supported (int 10h)",
           "ACPI is supported", "USB legacy is supported",
           "BIOS boot specification is supported",
           "Function key-initiated network boot is supported``"]
    assert ret.get("bios_information")[0].get("characteristics") == tmp

    assert ret.get("system_information")[0].get("manufacturer") == "HP"
    assert ret.get("system_information")[0].get("product_name") == "ProLiant BL685c G1"
    assert ret.get("system_information")[0].get("version") == "Not Specified"
    assert ret.get("system_information")[0].get("serial_number") == "3H6CMK2537"
    assert ret.get("system_information")[0].get("uuid") == "58585858-5858-3348-3643-4D4B32353337"
    assert ret.get("system_information")[0].get("wake-up_type") == "Power Switch"
    assert ret.system_uuid == '58585858-5858-3348-3643-4D4B32353337'.lower()


def test_dmidecode_oddities():
    dmi = DMIDecode(context_wrap(DMIDECODE_ODDITIES))

    assert len(dmi['oem-specific_type']) == 3
    assert dmi['oem-specific_type'][0] == {
        'header_and_data': '81 08 09 00 01 01 02 01',
        'strings': ['Intel_ASF', 'Intel_ASF_001'],
    }
    assert dmi['oem-specific_type'][1] == {
        'header_and_data': '86 0D 0A 00 28 06 14 20 00 00 00 00 00',
    }
    assert dmi['oem-specific_type'][2] == {
        'header_and_data': '01 02 03 04 05 06 07 08',
    }

    assert len(dmi['port_connector_information']) == 2
    assert dmi['port_connector_information'][0] == {
        'internal_reference_designator': 'Not Available',
        'internal_connector_type': 'None',
        'external_reference_designator': 'USB 1',
        'external_connector_type': 'Access Bus (USB)',
        'port_type': 'USB',
    }
    assert dmi['port_connector_information'][0] == {
        'internal_reference_designator': 'Not Available',
        'internal_connector_type': 'None',
        'external_reference_designator': 'USB 1',
        'external_connector_type': 'Access Bus (USB)',
        'port_type': 'USB',
    }

    assert len(dmi['bios_language_information']) == 1
    assert dmi['bios_language_information'][0] == {
        'language_description_format': 'Abbreviated',
        'installable_languages': ['1', 'en-US'],
        'currently_installed_language': 'en-US'
    }
