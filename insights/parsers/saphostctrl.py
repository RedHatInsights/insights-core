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
class SAPHostCtrlInstances(CommandParser):
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
        >>> sap_inst.data[-1]['CreationClassName']
        'SAPInstance'
        >>> sap_inst.data[-1]['SID']
        'D90'
        >>> sap_inst.data[-1]['SapVersionInfo']  # Note: captured as one string
        '749, patch 211, changelist 1754007'
        >>> sap_inst.data[0]['InstanceType']  # Inferred code from InstanceName
        'HDB'

    Attributes:
        data (list): List of dicts where keys are the lead name of each line and
            values are the string value.
        instances (list): The list of instances found in the cluster output.
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
        if len(content) == 1:
            raise ParseException("Incorrect content: '{0}'".format(content))

        self.data = []
        self.instances = []
        _current_instance = {}
        _sids = set()
        _types = set()

        def _update_instance(inst):
            for _dir in self.REQUIRED_DIRECTIVES:
                if _dir not in inst:
                    raise ParseException('Missing: "{0}"'.format(_dir))

            if not inst['InstanceName'].endswith(inst['SystemNumber']):
                raise ParseException(
                    'InstanceName: "{0}" missing match with SystemNumber: "{0}"'.format(inst['InstanceName'], inst['SystemNumber']))
            # InstanceType = The chars in InstanceName before the SystemNumber
            # subtract len(sysnumber) characters from instance name
            inst['InstanceType'] = inst['InstanceName'][0:-len(inst['SystemNumber'])]

        _current_instance = {}
        for line in (l.strip() for l in content):
            if line.startswith('******'):
                # Skip separator lines but save and reset current instance
                if _current_instance:
                    _update_instance(_current_instance)
                    self.instances.append(_current_instance['InstanceName'])
                    self.data.append(_current_instance)
                    _types.add(_current_instance['InstanceType'])
                    _sids.add(_current_instance['SID'])
                _current_instance = {}
                continue
            fields = [i.strip() for i in line.split(',', 2)]
            if len(fields) < 3:
                raise ParseException("Incorrect line: '{0}'".format(line))
            # TODO: if we see something other than 'String' in the second
            # field, we could maybe change its type, say to an integer?
            _current_instance[fields[0]] = fields[2]
        # the last instance
        if _current_instance:
            _update_instance(_current_instance)
            self.instances.append(_current_instance['InstanceName'])
            self.data.append(_current_instance)
            _types.add(_current_instance['InstanceType'])
            _sids.add(_current_instance['SID'])
        self.sids = list(_sids)
        self.types = list(_types)

    def __len__(self):
        return len(self.data)
