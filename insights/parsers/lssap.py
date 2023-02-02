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
    >>> lssap.instances
    ['D16', 'D22', 'D50', 'D51']
    >>> lssap.version('D51')
    '749, patch 10, changelist 1698137'
    >>> lssap.is_hana()
    False
    >>> lssap.data[3]['Instance']
    'D51'
"""
from insights.core import CommandParser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.parsers import parse_delimited_table
from insights.specs import Specs


@parser(Specs.lssap)
class Lssap(CommandParser):
    """Class to parse ``lssap`` command output.

    Raises:
        SkipComponent: Nothing needs to be parsed.
        ParseException: Raised if any error occurs parsing the content.

    Attributes:
        data (list): List of dicts, where the keys in each dict are the column
            headers and each item in the list represents a SID.
        sid (list): List of the SIDs from the SID column.
        instances (list): List of instances running on the system.
        instance_types (list): List of instance types running on the system.
    """
    def parse_content(self, content):
        if not content:
            raise SkipComponent()

        self.data = []
        # remove lssap version and bar text from content
        start_ndx = end_index = -1
        for i, l in enumerate(content):
            if start_ndx == -1 and l.lstrip().startswith("========"):
                start_ndx = i
                continue
            if end_index == -1 and l.strip().startswith("========"):
                end_index = i
                break
        if start_ndx == -1 or end_index == -1:
            raise ParseException("Lssap: Unable to parse {0} line(s) of content: ({1})".format(len(content), content))

        clean_content = content[start_ndx + 1:end_index]
        if len(clean_content) > 0 and clean_content[0].lstrip().startswith("SID"):
            self.data = parse_delimited_table(clean_content, delim='|', header_delim=None)
        else:
            raise ParseException("Lssap: Unable to parse {0} line(s) of content: ({1})".format(len(content), content))

        self.sid = sorted(set(row["SID"] for row in self.data if "SID" in row))
        self.instances = [row["Instance"] for row in self.data if "Instance" in row]
        self.instance_types = sorted(set(inst.rstrip('1234567890') for inst in self.instances))

    def version(self, instance):
        """str: returns the Version column corresponding to the ``instance`` in
        Instance or ``None`` if ``instance`` is not found.
        """
        for row in self.data:
            if instance == row['Instance']:
                return row["Version"]

    def is_netweaver(self):
        """bool: Is any SAP NetWeaver instance detected?"""
        return 'D' in self.instance_types

    def is_hana(self):
        """bool: Is any SAP HANA instance detected?"""
        return 'HDB' in self.instance_types

    def is_ascs(self):
        """bool: Is any SAP System Central Services instance detected?"""
        return 'ASCS' in self.instance_types
