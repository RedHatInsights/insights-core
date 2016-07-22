from falafel.mappers import dmidecode
from falafel.tests import context_wrap

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


class TestDmidecode():

    def test_get_dmidecode(self):
        '''
        Test for three kinds of output format of dmidecode shared_mapper
        '''
        context = context_wrap(DMIDECODE)
        ret = dmidecode.get_dmidecode(context)

        assert ret.get("bios_information").get("vendor") == "HP"
        assert ret.get("bios_information").get("version") == "P70"
        assert ret.get("bios_information").get("release_date") == "03/01/2013"
        assert ret.get("bios_information").get("address") == "0xF0000"
        assert ret.get("bios_information").get("runtime_size") == "64 kB"
        assert ret.get("bios_information").get("rom_size") == "8192 kB"

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
        assert ret.get("bios_information").get("characteristics") == tmp
        assert ret.get("bios_information").get("firmware_revision") == "1.22"

        assert ret.get("system_information").get("manufacturer") == "HP"
        assert ret.get("system_information").get("product_name") == "ProLiant DL380p Gen8"
        assert ret.get("system_information").get("version") == "Not Specified"
        assert ret.get("system_information").get("serial_number") == "2M23360006"
        assert ret.get("system_information").get("uuid") == "34373936-3439-4D32-3233-333630303036"
        assert ret.get("system_information").get("wake-up_type") == "Power Switch"
        assert ret.get("system_information").get("sku_number") == "697494-S01"
        assert ret.get("system_information").get("family") == "ProLiant"

        assert ret.get("chassis_information").get("manufacturer") == "hp"
        assert ret.get("chassis_information").get("type") == "rack mount chassis"
        assert ret.get("chassis_information").get("lock") == "not present"
        assert ret.get("chassis_information").get("version") == "not specified"
        assert ret.get("chassis_information").get("serial_number") == "2m23360006"
        assert ret.get("chassis_information").get("asset_tag") == ""
        assert ret.get("chassis_information").get("boot-up_state") == "Safe"
        assert ret.get("chassis_information").get("power_supply_state") == "Safe"
        assert ret.get("chassis_information").get("thermal_state") == "Safe"
        assert ret.get("chassis_information").get("security_status") == "Unknown"
        assert ret.get("chassis_information").get("oem_information") == "0x00000000"
        assert ret.get("chassis_information").get("height") == "2 U"
        assert ret.get("chassis_information").get("number_of_power_cords") == "2"
        assert ret.get("chassis_information").get("manufacturer") == "hp"
        assert ret.get("chassis_information").get("contained_elements") == "0"

    def test_get_dmidecode_fail(self):
        '''
        Test for faied raw data
        '''
        context = context_wrap(DMIDECODE_FAIL)
        ret = dmidecode.get_dmidecode(context)

        assert ret.present is False

    def test_get_dmidecode_v(self):
        '''
        Test for get_virt()
        '''
        context = context_wrap(DMIDECODE_V)
        ret = dmidecode.get_dmidecode(context)
        assert ret.present is True
        assert ret.virt_what == "vmware"

    def test_get_dmidecode_dmi(self):
        '''
        Test for three kinds of output format of dmidecode shared_mapper
        with special input format:
        "\n\tDMI" in the input
        '''
        context = context_wrap(DMIDECODE_DMI)
        ret = dmidecode.get_dmidecode(context)

        assert ret.get("bios_information").get("vendor") == "HP"
        assert ret.get("bios_information").get("version") == "A08"
        assert ret.get("bios_information").get("release_date") == "09/27/2008"
        assert ret.get("bios_information").get("address") == "0xF0000"
        assert ret.get("bios_information").get("runtime_size") == "64 kB"
        assert ret.get("bios_information").get("rom_size") == "4096 kB"

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
        assert ret.get("bios_information").get("characteristics") == tmp

        assert ret.get("system_information").get("manufacturer") == "HP"
        assert ret.get("system_information").get("product_name") == "ProLiant BL685c G1"
        assert ret.get("system_information").get("version") == "Not Specified"
        assert ret.get("system_information").get("serial_number") == "3H6CMK2537"
        assert ret.get("system_information").get("uuid") == "58585858-5858-3348-3643-4D4B32353337"
        assert ret.get("system_information").get("wake-up_type") == "Power Switch"
