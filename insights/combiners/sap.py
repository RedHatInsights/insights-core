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

SAPInstances = namedtuple(
    "SAPInstances",
    field_names=["name", "hostname", "sid", "type", "full_type", "number", "fqdn", "version"])
"""namedtuple: Type for storing the SAP instance."""

DAA_TYPES = {
    'Solution Manager Diagnostic Agent': ['SMDA'],
    'Diagnostic Agent': ['DAA', 'SMD'],
}
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
        >>> len(saps.instances)
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
        self._local_instances = []
        self._instances = []
        self._daa_instances = []

        self._types = insts.types
        self._all_instances = insts.instances
        for inst in insts:
            k = inst['InstanceName']
            if (hn == inst['Hostname'].split('.')[0] or
                    fqdn == inst['FullQualifiedHostname'] or
                    fqdn == inst['Hostname']):
                self._local_instances.append(k)
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
            if (
                i.full_type in DAA_TYPES or
                i.type in [st for sts in DAA_TYPES.values() for st in sts]
            ):
                self._daa_instances.append(i.name)
            else:
                self._instances.append(i.name)

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
    def all_instances(self):
        """
        list: List of all the SAP instances listed by the command.
        """
        return self._all_instances

    @property
    def instances(self):
        """
        list: List of the SAP instances that are NOT Diagnostic Agent
              instance, e.g. HANA, NetWeaver, ASCS, or other instances
        """
        return self._instances

    @property
    def daa_instances(self):
        """
        list: List of the SAP Diagnostic Agent instances, e.g.
              Diagnostics Agents: SMDA97/SMDA98
        """
        return self._daa_instances

    @property
    def function_instances(self):
        """
        .. warning::
            This property is deprecated and will be removed from 3.6.0.
            It's recommended to use the `daa_instances` attribute of
            :class:`insights.combiners.sap.Sap` instead.

        list: List of functional SAP instances.
        """
        return self.daa_instances

    @property
    def business_instances(self):
        """
        .. warning::
            This property is deprecated and will be removed from 3.6.0.
            It's recommended to use the `instances` attribute of
            :class:`insights.combiners.sap.Sap` instead.

        list: List of business SAP instances.
        """
        return self.instances

    @property
    def local_instances(self):
        """
        .. warning::
            This property is deprecated and will be removed from 3.6.0.

        List: List of all SAP instances running on this host.
        """
        return self._local_instances

    @property
    def data(self):
        """
        .. warning::
            This property is deprecated and will be removed from 3.6.0.

        dict: Dict with the instance name as the key and instance details as the value.
        """
        return self
