"""
Sap
===
This combiner combines the following parsers for SAP instances:
:class:`insights.parsers.saphostctrl.SAPHostCtrlInstances` and
:class:`insights.parsers.hostname.Hostname`
"""
from collections import namedtuple

from insights import SkipComponent
from insights.combiners.hostname import Hostname
from insights.core.plugins import combiner
from insights.parsers.saphostctrl import SAPHostCtrlInstances

SAPInstances = namedtuple("SAPInstances",
        field_names=["name", "hostname", "sid", "type", "full_type", "number", "fqdn", "version"])
"""namedtuple: Type for storing the SAP instance."""

FUNC_FULL_TYPES = [
    'Solution Manager Diagnostic Agent',
    'Diagnostic Agent'
]
NETW_TYPES = ('D', 'ASCS', 'DVEBMGS', 'J', 'SCS', 'ERS', 'W', 'G', 'JC')
"""
tuple: Tuple of the prefix string of the functional SAP instances::

    D      :    NetWeaver (ABAP Dialog Instance)
    ASCS   :    NetWeaver (ABAP Central Services)
    DVEBMGS:    NetWeaver (Primary Application server)
    J      :    NetWeaver (Java App Server Instance)
    SCS    :    NetWeaver (Java Central Services)
    ERS    :    NetWeaver (Enqueue Replication Server)
    W      :    NetWeaver (WebDispatcher)
    G      :    NetWeaver (Gateway)
    JC     :    NetWeaver (Java App Server Instance)
"""


@combiner(Hostname, SAPHostCtrlInstances)
class Sap(dict):
    """
    It combines the following parsers for SAP instances:
    :class:`insights.parsers.saphostctrl.SAPHostCtrlInstances` and
    :class:`insights.parsers.hostname.Hostname`

    Attributes:
        all_instances (list): List of all the SAP instances listed by the command.
        function_instances (list): List of functional SAP instances
                                   E.g. Diagnostics Agents SMDA97/SMDA98
        business_instances (list): List of business SAP instances
                                   E.g. HANA, NetWeaver, ASCS, or others
        local_instances (list): List of all SAP instances running on this host

    Examples:
        >>> type(saps)
        <class 'insights.combiners.sap.Sap'>
        >>> 'DVEBMGS12' in saps
        True
        >>> saps['DVEBMGS12'].number
        '12'
        >>> saps.sid('ASCS10')
        'R4D'
        >>> saps.hostname('ASCS10')
        'host_1'
        >>> len(saps.business_instances)
        3
        >>> saps.is_hana
        False
        >>> saps.is_netweaver
        True
        >>> saps.is_ascs
        True
    """
    def __init__(self, hostname, insts):
        hn = hostname.hostname
        fqdn = hostname.fqdn
        self.local_instances = []
        self.business_instances = []
        self.function_instances = []
        self.all_instances = []
        self._types = set()
        if insts:
            self._types = insts.types
            self.all_instances = insts.instances
            for inst in insts:
                k = inst['InstanceName']
                if (hn == inst['Hostname'].split('.')[0] or
                        fqdn == inst['FullQualifiedHostname'] or
                        fqdn == inst['Hostname']):
                    self.local_instances.append(k)
                self[k] = SAPInstances(k,
                                       inst['Hostname'],
                                       inst['SID'],
                                       inst['InstanceName'].strip('1234567890'),
                                       inst['InstanceType'],
                                       inst['SystemNumber'],
                                       inst['FullQualifiedHostname'],
                                       inst['SapVersionInfo'])
        if len(self) == 0:
            raise SkipComponent('No SAP instance.')

        for i in self.values():
            (self.function_instances
                if i.full_type in FUNC_FULL_TYPES else
                    self.business_instances).append(i.name)

    def version(self, instance):
        """str: Returns the version of the ``instance``."""
        return self[instance].version if instance in self else None

    def sid(self, instance):
        """str: Returns the sid of the ``instance``."""
        return self[instance].sid if instance in self else None

    def type(self, instance):
        """str: Returns the short type code of the ``instance``."""
        return self[instance].type if instance in self else None

    def full_type(self, instance):
        """str: Returns the full type code of the ``instance``."""
        return self[instance].full_type if instance in self else None

    def hostname(self, instance):
        """str: Returns the hostname of the ``instance``."""
        return self[instance].hostname if instance in self else None

    def number(self, instance):
        """str: Returns the systeme number of the ``instance``."""
        return self[instance].number if instance in self else None

    @property
    def is_netweaver(self):
        """bool: Is any SAP NetWeaver instance detected?"""
        return any(_t in self._types for _t in NETW_TYPES)

    @property
    def is_hana(self):
        """bool: Is any SAP HANA instance detected?"""
        return 'HDB' in self._types

    @property
    def is_ascs(self):
        """bool: Is any ABAP Central Services instance detected?"""
        return 'ASCS' in self._types

    @property
    def data(self):
        """dict: Dict with the instance name as the key and instance details as the value."""
        return self
