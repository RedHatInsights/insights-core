"""
DMIDecode - Command ``dmidecode``
=================================

Parses the output of the ``dmidecode`` command to catalogue the hardware
associated with the system.

In general, DMIdecode recognizes the sections of device information,
separated by blank lines, processed in the following way.

* It uses the descriptor line that precedes the indented device information
  (e.g. 'BIOS Information') as the name for that section, converting the name
  into lower case and replacing spaces with underscores (e.g.
  'bios_information') to look more Pythonic.

* Within each section, data is split up on colons.

* Lines such as 'Characteristics' that end with a colon and have one or more
  further indented lines after them are converted into a list of the values so
  indented.

The common information retrieved from dmidecode is available in several
convenience properties:

* **system_info** - Information about the machine itself
* **bios** - the BIOS information
* **bios_vendor** - the BIOS's 'Vendor' attribute
* **bios_date** - the BIOS's 'Release Date' attribute
* **processor_manufacturer** - the processor's 'Manufacturer' attribute
* **is_present** - this indicates whether dmidecode information was found.

Sample input::

    # dmidecode 2.2
    SMBIOS 2.4 present.
    104 structures occupying 3162 bytes.
    Table at 0x000EE000.
    Handle 0x0000
        DMI type 0, 24 bytes.
        BIOS Information
            Vendor: HP
            Version: A08
            Release Date: 09/27/2008
            Address: 0xF0000
            Runtime Size: 64 kB
            ROM Size: 4096 kB
            Characteristics:
                PCI is supported
                PNP is supported
                BIOS is upgradeable
                BIOS shadowing is allowed
                ESCD support is available
                Boot from CD is supported
                Selectable boot is supported
                EDD is supported
                5.25"/360 KB floppy services are supported (int 13h)
                5.25"/1.2 MB floppy services are supported (int 13h)
                3.5"/720 KB floppy services are supported (int 13h)
                Print screen service is supported (int 5h)
                8042 keyboard services are supported (int 9h)
                Serial services are supported (int 14h)
                Printer services are supported (int 17h)
                CGA/mono video services are supported (int 10h)
                ACPI is supported
                USB legacy is supported
                BIOS boot specification is supported
                Function key-initiated network boot is supported``
    Handle 0x0100
        DMI type 1, 27 bytes.
        System Information
            Manufacturer: HP
            Product Name: ProLiant BL685c G1
            Version: Not Specified
            Serial Number: 3H6CMK2537
            UUID: 58585858-5858-3348-3643-4D4B32353337
            Wake-up Type: Power Switch

Examples:

    >>> dmi = shared[DMIDecode]
    >>> dmi.is_present
    True
    >>> len(dmi['bios_information'])
    1
    >>> dmi['bios_information'][0]['vendor']
    'HP'
    >>> dmi.bios_vendor
    'HP'
    >>> dmi.bios_date
    datetime.date(2008, 9, 27)
    >>> len(dmi.bios['characteristics'])
    20
    >>> dmi.bios['characteristics'][0]
    'PCI is supported'
    >>> dmi.system_uuid == '58585858-5858-3348-3643-4D4B32353337'
    True
"""
import re
import uuid

from datetime import date

from insights import LegacyItemAccess, parser, defaults, CommandParser
from insights.specs import Specs


@parser(Specs.dmidecode)
class DMIDecode(CommandParser, LegacyItemAccess):
    """
    Class for DMI information.
    """

    def parse_content(self, content):
        self.data = parse_dmidecode(content, pythonic_keys=True)

    @property
    def system_info(self):
        """(str): Convenience method to get system information"""
        return self["system_information"][0] if "system_information" in self else None

    @property
    @defaults()
    def system_uuid(self):
        """(str): Convenience method to get system UUID"""
        sys_uuid = self["system_information"][0]['uuid']
        return str(uuid.UUID(sys_uuid))

    @property
    def bios(self):
        """(str): Convenience method to get BIOS information"""
        return self["bios_information"][0] if "bios_information" in self else None

    @property
    @defaults()
    def bios_vendor(self):
        """(str): Convenience method to get BIOS vendor"""
        return self["bios_information"][0]["vendor"]

    @property
    @defaults()
    def bios_date(self):
        """(datetime.date): Get the BIOS release date in datetime.date format"""
        month, day, year = map(int, self["bios_information"][0]["release_date"].split("/"))
        return date(year, month, day)

    @property
    @defaults()
    def processor_manufacturer(self):
        """(str): Convenience method to get the processor manufacturer"""
        return self["processor_information"][0]["manufacturer"]

    @property
    def is_present(self):
        """(bool): Is there any decodable data in the content?"""
        return bool(self.data)


def parse_dmidecode(dmidecode_content, pythonic_keys=False):
    """
    Returns a dictionary of dmidecode information parsed from a dmidecode list
    (i.e. from context.content)

    This method will attempt to handle leading spaces rather than tabs.
    """
    if len(dmidecode_content) < 3:
        return {}

    section = None
    obj = {}
    current = {}

    buf = "\n".join(dmidecode_content).strip()

    # Some versions of DMIDecode have an extra
    # level of indentation, as well as slightly
    # different configuration for each section.
    if "\tDMI type" in buf:
        pat = re.compile("^\t", flags=re.MULTILINE)
        buf = pat.sub("", buf)

        buf = buf.replace("\nDMI type", "DMI type")
        buf = buf.replace("\nHandle", "\n\nHandle")

    buf = buf.replace("\n\t\t", "\t")

    def fix_key(k):
        return k.lower().replace(" ", "_") if pythonic_keys else k

    for line in buf.splitlines():
        nbline = line.strip()
        if section:
            if not nbline:
                # There maybe some sections with the same name, such as:
                # processor_information
                if section in obj:
                    obj[section].append(current)
                else:
                    obj[section] = [current]
                current = {}
                section = key = None
                continue

            elif line.startswith("\t"):
                if ":" in line:
                    key, value = nbline.split(":", 1)
                    key = fix_key(key)
                    value = value.strip()

                if "\t" in value:
                    current[key] = list(filter(None, value.split("\t")))
                else:
                    current[key] = value
            else:
                section = None

        if not section:
            # Ignore 'Table at 0xBFFCB000' and similar.
            if not ('Table' in nbline or 'table' in nbline):
                section = fix_key(nbline)

    if section in obj:
        obj[section].append(current)
    else:
        obj[section] = [current]

    return obj
