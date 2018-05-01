"""
SAPHostInstances - command ``/usr/sap/hostctrl/exe/saphostctrl -function GetCIMObject -enuminstances SAPInstance``
==================================================================================================================

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
    >>> instances = shared[SAPHostInstances]
    >>> len(instances.data)
    2
    >>> h1 = instances.data[0]
    >>> h1['CreationClassName']
    'SAPInstance'
    >>> h1['SID']
    'D89'
    >>> h1['SapVersionInfo']  # Note: captured as one string
    '749, patch 211, changelist 1754007'
    >>> h1['instance_code']  # Inferred code from InstanceName
    'HDB'
    >>> h1['instance_type']  # note lower case for inferred data
    'hana'
    >>> svcs_list = instances.search(FullQualifiedHostname__contains='svcs.example.com')  # Find instances by listed properties
    >>> len(svcs_list)
    0
    >>> d_list = instances.search(instance_type='hana')  # Find instances by derived properties
    >>> d_list[0] == h1  # List contains instances
    True

"""
from .. import parser
from .lssap import Lssap
from insights.parsers import keyword_search
from insights.specs import Specs


@parser(Specs.saphostctl_getcimobject_sapinstance)
class SAPHostInstances(Lssap):
    """
    This class provides processing for the output of the
    ``/usr/sap/hostctrl/exe/saphostctrl -function GetCIMObject -enuminstances SAPInstance``
    command on SAP systems.

    Attributes:
        data (list): List of dicts, where the keys in each dict are the
            heading names and each item in the list represents a SID.
        running_inst_types (set): The set of instance types found in the
            cluster output.
        ignored_lines (list): Data lines that could not be parsed because they
            did not have the right number of fields.
    """
    def parse_content(self, content):
        self.data = []
        self.running_inst_types = set()
        self.ignored_lines = []
        current_instance = {}

        def update_instance_and_append(inst):
            # This update and append is done twice - once when a new section
            # is started and once at the end of the file.  So it's better to
            # have it as a single function than to copy and paste the code.
            # Add Lssap compatibility keys - allow override
            if 'InstanceName' in inst and 'Instance' not in inst:
                inst['Instance'] = inst['InstanceName']
            if 'SapVersionInfo' in inst and 'Version' not in inst:
                inst['Version'] = inst['SapVersionInfo']
            # Add inferred data to current instance dict
            # instance_type = the bit in SID before the SystemNumber
            if (
                'InstanceName' in inst and
                'SystemNumber' in inst and
                inst['InstanceName'].endswith(
                    inst['SystemNumber']
                )
            ):
                # subtract len(sysnumber) characters from instance name
                itype = inst['InstanceName'][0:-len(
                    inst['SystemNumber']
                )]
                inst['instance_code'] = itype
                if itype in self.instance_dict:
                    inst['instance_type'] = self.instance_dict[itype]
                    self.running_inst_types.add(itype)
            # Now save the complete instance
            self.data.append(inst)

        for line in (l.strip() for l in content):
            if line.startswith('********'):
                # Skip separator lines but save and reset current instance
                if current_instance:
                    update_instance_and_append(current_instance)
                current_instance = {}
                continue
            fields = line.split(' , ', 2)
            # Ignore lines that have less than three fields in them
            if len(fields) < 3:
                self.ignored_lines.append(line)
                continue
            key, value = fields[0], fields[2]
            # TODO: if we see something other than 'String' in the second
            # field, we could maybe change its type, say to an integer?
            current_instance[key] = value

        # There's no final line, so capture the current instance if we have one
        if current_instance:
            update_instance_and_append(current_instance)

    # Lssap-compatible properties brought in by subclassing

    def search(self, *args, **search_args):
        """
        Search for the given key/value pairs in the data.  Please refer to the
        :py:meth:`insights.parsers.keyword_search` function documentation for
        a more complete description of how to use this.

        Field names are searched as is, including case.

        Examples:
            >>> d_list = instances.search(instance_type='hana')  # Find instances by derived properties
            >>> d_list[0] == instances.data[0]  # List contains instances
            True
            >>> len(instances.search(SapVersionInfo__contains='changelist 1779613'))
            0

        """
        return keyword_search(self.data, **search_args)
