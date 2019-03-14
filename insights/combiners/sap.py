"""
Sap - Combiner
==============

This combiner gets the running SAP instances on the system based on below
logic::

    if (SAPLOCALHOST = 'hostname') && InstanceType = D## ) then
        on this system runs SAP Netweaver Application Server version

    if (SAPLOCALHOST = 'hostname') && InstanceType = ASCS## ) then
        on this system runs SAP Netweaver Application Server Central Instance
        version

    if (SAPLOCALHOST = 'hostname') && InstanceType = HDB## ) then
        on this system runs SAP HANA database version

Check settings according SAP Notes compiled here:
https://wiki.scn.sap.com/wiki/x/rDK7Gg

"""

from collections import namedtuple
from insights import LegacyItemAccess
from insights.parsers import SkipException
from insights.core.plugins import combiner
from insights.combiners.hostname import hostname
from insights.parsers.lssap import Lssap
from insights.parsers.saphostctrl import SAPHostCtrlInstances


SAPInstances = namedtuple("SAPInstances",
        field_names=["name", "hostname", "sid", "type", "number", "version"])
"""namedtuple: Type for storing the SAP instance."""


@combiner(hostname, optional=[SAPHostCtrlInstances, Lssap])
class Sap(LegacyItemAccess):
    """
    Combiner for analyzing the SAP instances running on the system.

    Prefer SAPHostCtrlInstances to Lssap.

    Examples:
        >>> type(saps)
        <class 'insights.combiners.sap.Sap'>
        >>> saps['D16'].number
        '16'
        >>> saps.sid('HDB16')
        'HA2'
        >>> saps.hostname('HDB16')
        'lu0417'
        >>> 'D22' in saps.local_instances
        False
        >>> len(saps.business_instances)
        2
        >>> saps.is_hana
        True
        >>> saps.is_netweaver
        True
        >>> saps.is_ascs
        False

    Attributes:
        all_instances (list): List of all the SAP instances listed by the command.
        local_instances (list): List of SAP instances which are running on the system.
        function_instances (list): List of function SAP instances running on the system.
                                   E.g. Diagnostics Agents SMDA97/SMDA98
        business_instances (list): List of business SAP instances running on the system.
                                   E.g. HANA, NetWeaver, ASCS, or others
    """
    def __init__(self, hostname, insts, lssap):
        hn = hostname.hostname
        self.data = {}
        self.local_instances = []
        self.business_instances = []
        self.function_instances = []
        self.all_instances = []
        self._types = set()
        if insts:
            for inst in insts.data:
                k = inst['InstanceName']
                self.all_instances.append(k)
                if hn == inst['Hostname']:
                    self.local_instances.append(k)
                    self._types.add(inst['InstanceType'])
                self.data[k] = SAPInstances(k,
                                            inst['Hostname'],
                                            inst['SID'],
                                            inst['InstanceType'],
                                            inst['SystemNumber'],
                                            inst['SapVersionInfo'])
        elif lssap:
            for inst in lssap.data:
                k = inst['Instance']
                t = k.rstrip('1234567890')
                self.all_instances.append(k)
                if hn == inst['SAPLOCALHOST']:
                    self.local_instances.append(k)
                    self._types.add(t)
                self.data[k] = SAPInstances(k,
                                            inst['SAPLOCALHOST'],
                                            inst['SID'],
                                            t,
                                            inst['Nr'],
                                            inst['Version'])
        else:
            raise SkipException('No SAP instance.')

        FUNC_INSTS = ('SMDA')
        for i in self.local_instances:
            (self.function_instances if i.startswith(FUNC_INSTS) else self.business_instances).append(i)

    def version(self, instance):
        """str: Returns the version of the ``instance``."""
        return self.data[instance].version if instance in self.data else None

    def sid(self, instance):
        """str: Returns the sid of the ``instance``."""
        return self.data[instance].sid if instance in self.data else None

    def type(self, instance):
        """str: Returns the type code of the ``instance``."""
        return self.data[instance].type if instance in self.data else None

    def hostname(self, instance):
        """str: Returns the hostname of the ``instance``."""
        return self.data[instance].hostname if instance in self.data else None

    def number(self, instance):
        """str: Returns the systeme number of the ``instance``."""
        return self.data[instance].number if instance in self.data else None

    @property
    def is_netweaver(self):
        """bool: SAP NetWeaver is running on the system."""
        return 'D' in self._types

    @property
    def is_hana(self):
        """bool: SAP Hana is running on the system."""
        return 'HDB' in self._types

    @property
    def is_ascs(self):
        """bool: SAP System Central Services is running on the system."""
        return 'ASCS' in self._types
