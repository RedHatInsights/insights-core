"""
SAPHostCtrlInstances - Commands ``saphostctrl``
===============================================
"""
from insights.core import CommandParser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.filters import add_filter
from insights.core.plugins import parser
from insights.specs import Specs


SAP_INST_FILTERS = [
        '******',
        'SID',
        'SystemNumber',
        'InstanceName',
        'InstanceType',
        'Hostname',
        'SapVersionInfo',
        'FullQualifiedHostname'
]
add_filter(Specs.saphostctl_getcimobject_sapinstance, SAP_INST_FILTERS)


@parser(Specs.saphostctl_getcimobject_sapinstance)
class SAPHostCtrlInstances(CommandParser, list):
    """
    This class provides processing for the output of the
    ``saphostctrl -function GetCIMObject -enuminstances SAPInstance``
    command on SAP systems.

    Sample output of the command::

        *********************************************************
         SID , String , D89
         SystemNumber , String , 88
         InstanceName , String , HDB88
         InstanceType , String , HANA Test
         Hostname , String , hdb88
         FullQualifiedHostname , String , hdb88.example.com
         IPAddress , String , 10.0.0.88
         SapVersionInfo , String , 749, patch 211, changelist 1754007
        *********************************************************
         SID , String , D90
         SystemNumber , String , 90
         InstanceName , String , HDB90
         InstanceType , String , HANA Test
         Hostname , String , hdb90
         FullQualifiedHostname , String , hdb90.example.com
         IPAddress , String , 10.0.0.90
         SapVersionInfo , String , 749, patch 211, changelist 1754007

    Examples:
        >>> type(sap_inst)
        <class 'insights.parsers.saphostctrl.SAPHostCtrlInstances'>
        >>> sap_inst[1]['SID']
        'D90'
        >>> sap_inst[0]['SapVersionInfo']
        '749, patch 211, changelist 1754007'
        >>> sap_inst[1]['InstanceType']
        'HANA Test'
        >>> sap_inst.types
        ['HDB']
        >>> sorted(sap_inst.sids)
        ['D89', 'D90']

    Raises:
        SkipComponent: When input is empty.
        ParseException: When input cannot be parsed.
    """
    def parse_content(self, content):
        self._instances = []
        self._sids = set()
        self._types = set()

        inst = {}
        for line in content:
            line = line.strip()
            if not line:
                continue
            if line.startswith('******'):
                inst = {}
                self.append(inst)
                continue

            fields = [i.strip() for i in line.split(',', 2)]
            if len(fields) < 3:
                raise ParseException("Incorrect line: '{0}'".format(line))

            inst[fields[0]] = fields[2]

            if fields[0] == 'InstanceName':
                short_type = fields[2].strip('0123456789')
                # Back forward compatible: a short InstanceType was from the InstanceName
                if 'InstanceType' not in inst:
                    inst.update(InstanceType=short_type)
                self._instances.append(fields[2])
                self._types.add(short_type)

            self._sids.add(fields[2]) if fields[0] == 'SID' else None

        if len(self) < 1:
            raise SkipComponent("Nothing need to parse")

    @property
    def instances(self):
        """
        (list): The list of instances found in the cluster output.
        """
        return self._instances

    @property
    def sids(self):
        """
        (list): The list of SID found in the cluster output.
        """
        return sorted(self._sids)

    @property
    def types(self):
        """
        (list): The list of short instance types.  The short instance
                type is set as the characters of the `InstanceName` before
                the `SystemNumber`.
        """
        return sorted(self._types)

    @property
    def data(self):
        """
        (list): List of dicts where keys are the lead name of each line and
                values are the string value.
        """
        return self
