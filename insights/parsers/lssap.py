"""
Lssap - command ``/usr/sap/hostctrl/exe/lssap``
===============================================

This module provides processing for the output of the ``lssap`` command on
SAP systems. The spec handled by this command inlude::

    "lssap"                     : CommandSpec("/usr/sap/hostctrl/exe/lssap")

Class ``Lssap`` parses the output of the ``lssap`` command.  Sample
output of this command looks like::

 - lssap version 1.0 -
 ==========================================
   SID   Nr   Instance    SAPLOCALHOST                        Version                 DIR_EXECUTABLE
   HA2|  16|       D16|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/D16/exe
   HA2|  22|       D22|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/D22/exe
   HA2|  50|       D50|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/D50/exe
   HA2|  51|       D51|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/D51/exe

Examples:
    >>> lssap = shared[Lssap]
    >>> lssap.instances()
    ['D16', 'D22', 'D50', 'D51']
    >>> lssap.version('D51')
    '749, path 10, changelist 1698137'
    >>> lssap.is_instance()
    True
    >>> lssap.is_hana()
    False
    >>> lssap.data[3]
    {'SID': 'HA2', 'Nr': '51', 'Instance': 'D51', 'SAPLOCALHOST': 'lu0417',
     'Version': '749, path 10, changelist 1698137', 'DIR_EXECUTABLE': '/usr/sap/HA2/D51/exe'}
    >>> lssap.data[3]['Instance']
    'D51'
"""
from .. import parser, CommandParser
from insights.parsers import ParseException, parse_delimited_table
from insights.specs import Specs


@parser(Specs.lssap)
class Lssap(CommandParser):
    """Class to parse ``lssap`` command output.

    Attributes:
        data (list): List of dicts, where the keys in each dict are the column
            headers and each item in the list represents a SID.

    Raises:
        ParseException: Raised if any error occurs parsing the content.
    """
    instance_dict = {'D': 'netweaver',
                     'HDB': 'hana',
                     'ASCS': 'ascs'}

    def __init__(self, *args, **kwargs):
        self.data = []
        super(Lssap, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        # remove lssap version and bar text from content
        clean_content = content[2:-1]
        if len(clean_content) > 0 and "SID" in clean_content[0]:
            self.data = parse_delimited_table(clean_content, delim='|', header_delim=None)
        else:
            raise ParseException("Lssap: Unable to parse {0} line(s) of content: ({1})".format(len(content), content))

        self.running_inst_types = [row["Instance"].rstrip('1234567890') for row in self.data if "Instance" in row]

        invalid_inst = [i for i in self.running_inst_types if i not in self.instance_dict]

        if invalid_inst:
            raise ParseException("Lssap: Invalid instance parsed in content: {0}".format(invalid_inst))

    def version(self, instance):
        """str: returns the Version column corresponding to the ``instance`` in
        Instance or ``None`` if ``instance`` is not found.
        """
        for row in self.data:
            if instance == row['Instance']:
                return row["Version"]

    @property
    def instances(self):
        """list: List instances running on the system."""
        return [row["Instance"] for row in self.data if "Instance" in row]

    @property
    def sid(self):
        """list: Returns a list of the SIDs from the SID column."""
        return list(set(row["SID"] for row in self.data if "SID" in row))

    def is_netweaver(self):
        """bool: SAP Netweaver is running on the system."""
        return 'D' in list(set(self.running_inst_types) & set(self.instance_dict.keys()))

    def is_hana(self):
        """bool: SAP Hana is running on the system."""
        return 'HDB' in list(set(self.running_inst_types) & set(self.instance_dict.keys()))

    def is_ascs(self):
        """bool: SAP System Central Services is running on the system."""
        return 'ASCS' in list(set(self.running_inst_types) & set(self.instance_dict.keys()))
