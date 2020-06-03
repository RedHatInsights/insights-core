"""
saphostctrl - Commands ``saphostctrl``
======================================

Parsers included in this module are:

SAPHostCtrlInstances - Command ``saphostctrl -function GetCIMObject -enuminstances SAPInstance``
------------------------------------------------------------------------------------------------
"""
from insights import parser, CommandParser
from insights.parsers import ParseException, SkipException
from insights.specs import Specs
from insights.core.filters import add_filter


SAP_INST_FILTERS = [
        '******',
        'CreationClassName',
        'SID',
        'SystemNumber',
        'InstanceName',
        'Hostname',
        'SapVersionInfo',
        'FullQualifiedHostname'
]
add_filter(Specs.saphostctl_getcimobject_sapinstance, SAP_INST_FILTERS)


@parser(Specs.saphostctl_getcimobject_sapinstance)
class SAPHostCtrlInstances(CommandParser, list):
    """
    This class provides processing for the output of the
    ``/usr/sap/hostctrl/exe/saphostctrl -function GetCIMObject -enuminstances SAPInstance``
    command on SAP systems.

    Sample output of the command::

        *********************************************************
         CreationClassName , String , SAPInstance
         SID , String , D89
         SystemNumber , String , 88
         InstanceName , String , HDB88
         Hostname , String , hdb88
         FullQualifiedHostname , String , hdb88.example.com
         IPAddress , String , 10.0.0.88
         SapVersionInfo , String , 749, patch 211, changelist 1754007
        *********************************************************
         CreationClassName , String , SAPInstance
         SID , String , D90
         SystemNumber , String , 90
         InstanceName , String , HDB90
         Hostname , String , hdb90
         FullQualifiedHostname , String , hdb90.example.com
         IPAddress , String , 10.0.0.90
         SapVersionInfo , String , 749, patch 211, changelist 1754007

    Examples:
        >>> type(sap_inst)
        <class 'insights.parsers.saphostctrl.SAPHostCtrlInstances'>
        >>> sap_inst[-1]['CreationClassName']
        'SAPInstance'
        >>> sap_inst[-1]['SID']
        'D90'
        >>> sap_inst[-1]['SapVersionInfo']  # Note: captured as one string
        '749, patch 211, changelist 1754007'
        >>> sap_inst[0]['InstanceType']  # Inferred code from InstanceName
        'HDB'

    Attributes:
        data (list): List of dicts where keys are the lead name of each line and
            values are the string value.
        sids (list): The list of SID found in the cluster output.
        types (list): The list of instance types found in the cluster output.
    Raises:
        SkipException: When input is empty.
        ParseException: When input cannot be parsed.
    """
    REQUIRED_DIRECTIVES = (
        'CreationClassName',
        'SID',
        'SystemNumber',
        'InstanceName',
        'Hostname',
        'SapVersionInfo',
        'FullQualifiedHostname'
    )

    def parse_content(self, content):
        if not content:
            raise SkipException("Empty content")

        _current_instance = {}
        for line in content:
            line = line.strip()
            if line.startswith('******'):
                _current_instance = {}
                self.append(_current_instance)
            else:
                fields = [i.strip() for i in line.split(',', 2)]
                if len(fields) < 3:
                    raise ParseException("Incorrect line: '{0}'".format(line))
                _current_instance[fields[0]] = fields[2]

        if len(self) == 0:
            raise SkipException()

        self._sids = []
        self._types = []
        self._instances = []
        for inst in self:
            name = inst.get('InstanceName', '')
            nr = inst.get('SystemNumber')
            if not (name and name.endswith(nr)):
                raise ParseException('Incorrect: InstanceName: "{0}", SystemNumber: "{0}"'.format(name, nr))
            # InstanceType = The chars in InstanceName before the SystemNumber
            # subtract len(sysnumber) characters from instance name
            inst['InstanceType'] = name[0:-len(nr)]
            self._sids.append(inst['SID'])
            self._types.append(inst['InstanceType'])
            self._instances.append(name)

    @property
    def sids(self):
        """
        Return the list of SAP ID of each SAP instance
        """
        return self._sids

    @property
    def types(self):
        """
        Return the list of instance type of each SAP instance
        """
        return self._types

    @property
    def instances(self):
        """
        Return the list of instance name of each SAP instance
        """
        return self._instances

    @property
    def data(self):
        """
        Return the list to keep backward compatibility
        """
        return self
