from insights.parsers.virt_what import VirtWhat as VWP
from insights.parsers.dmidecode import DMIDecode
from insights.combiners.virt_what import VirtWhat
from insights.tests import context_wrap

T1 = """
kvm
""".strip()

T2 = """

""".strip()

# occasionally we have 2 lines of output
T3 = """
xen
xen-dom0
aws
""".strip()

T4 = """
virt-what: virt-what-cpuid-helper program not found in $PATH
""".strip()

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


def test_vw_virt_what_1():
    vw = VWP(context_wrap(T1))
    dmi = DMIDecode(context_wrap(DMIDECODE_AWS))
    ret = VirtWhat(dmi, vw)
    assert ret.is_virtual is True
    assert ret.is_physical is False
    assert ret.generic == "kvm"


def test_vw_virt_what_2():
    vw = VWP(context_wrap(T2))
    dmi = DMIDecode(context_wrap(DMIDECODE_AWS))
    ret = VirtWhat(dmi, vw)
    assert ret.is_virtual is False
    assert ret.is_physical is True
    assert ret.generic == "baremetal"


def test_vw_virt_what_specific():
    vw = VWP(context_wrap(T3))
    dmi = DMIDecode(context_wrap(DMIDECODE_AWS))
    ret = VirtWhat(dmi, vw)
    assert ret.is_virtual is True
    assert ret.is_physical is False
    assert ret.generic == "xen"
    assert 'xen-dom0' in ret
    assert 'aws' in ret


def test_vw_dmidecode_1():
    vw = VWP(context_wrap(T4))
    dmi = DMIDecode(context_wrap(DMIDECODE_AWS))
    ret = VirtWhat(dmi, vw)
    assert ret.is_virtual is True
    assert ret.is_physical is False
    assert ret.generic == "xen"
    assert 'aws' in ret


def test_vw_dmidecode_2():
    vw = VWP(context_wrap(T4))
    dmi = DMIDecode(context_wrap(DMIDECODE))
    ret = VirtWhat(dmi, vw)
    assert ret.is_virtual is False
    assert ret.is_physical is True
    assert ret.generic == "baremetal"


def test_vw_dmidecode_3():
    vw = VWP(context_wrap(T4))
    dmi = DMIDecode(context_wrap(DMIDECODE_V))
    ret = VirtWhat(dmi, vw)
    assert ret.is_virtual is True
    assert ret.is_physical is False
    assert ret.generic == "vmware"


def test_vw_dmidecode_4():
    vw = VWP(context_wrap(T4))
    dmi = DMIDecode(context_wrap(DMIDECODE_KVM))
    ret = VirtWhat(dmi, vw)
    assert ret.is_virtual is True
    assert ret.is_physical is False
    assert ret.generic == "kvm"


def test_vw_dmidecode_5():
    dmi = DMIDecode(context_wrap(DMIDECODE_KVM))
    ret = VirtWhat(dmi, None)
    assert ret.is_virtual is True
    assert ret.is_physical is False
    assert ret.generic == "kvm"
