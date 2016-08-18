from falafel.core.plugins import mapper
from falafel.core import MapperOutput, computed
import re


@mapper('dmidecode')
class DMIDecode(MapperOutput):

    PRODUCT_MAP = {
        "VMware": "vmware",
        "KVM": "kvm",
        "domU": "xen",
        "Virtual Machine": "virtualpc"
    }

    MANUFACTURER_MAP = {
        "Microsoft Corporation": "virtualpc",
        "innotek GmbH": "virtualbox",
        "VMware": "vmware"
    }

    VENDOR_MAP = {
        "Parallels": "parallels",
        "QEMU": "qemu",
        "KVM": "kvm"
    }

    @staticmethod
    def parse_content(content):
        return parse_dmidecode(content, pythonic_keys=True)

    @computed
    def system_info(self):
        """Convenience method to get system information"""
        return self["system_information"][0] if "system_information" in self else None

    @computed
    def bios(self):
        """Convenience method to get BIOS information"""
        return self["bios_information"][0] if "bios_information" in self else None

    @computed
    def virt_what(self):
        '''
        Detect if this machine is running in a virtualized environment.
        Loosely based on `virt-what <http://people.redhat.com/~rjones/virt-what/>`_.

        If the virtualization environment is not actively trying to mask
        itself, its possible to detect the environment by looking at
        the ``product_name`` and ``vendor`` keys in ``dmidecode`` output.

        There are several ways and tricks to detect virtualized
        environments, but this function only focuses on using ``dmidecode``.
        As such, the argument to the function is expected to be a iterator
        containing the lines from a ``dmmidecode`` file.  This will usually
        be the ``content`` attribute from the context object passed to a
        mapper.

        The function returns the type of virtualized environment found, or
        ``None`` if virtualizion could not be determined.
        '''
        sys_info = self.get("system_information", [{}])[0]
        bios_info = self.get("bios_information", [{}])[0]

        product_name = sys_info.get("product_name")
        manufacturer = sys_info.get("manufacturer")
        vendor = bios_info.get("vendor")

        for dmidecode_value, mapping in [(product_name, self.PRODUCT_MAP),
                                         (manufacturer, self.MANUFACTURER_MAP),
                                         (vendor, self.VENDOR_MAP)]:
            for map_key in mapping:
                if dmidecode_value and map_key in dmidecode_value:
                    return mapping[map_key]

    @computed
    def is_present(self):
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
                else:
                    key = nbline
                    value = ""

                if "\t" in value:
                    current[key] = filter(None, value.split("\t"))
                else:
                    current[key] = value
            else:
                section = None

        if not section:
            section = fix_key(nbline)

    if section in obj:
        obj[section].append(current)
    else:
        obj[section] = [current]

    # Remove nonsense key-value
    for k in obj.keys():
        if "Table" in k or "table" in k:
            del obj[k]

    return obj
