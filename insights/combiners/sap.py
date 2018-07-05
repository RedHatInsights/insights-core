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

from insights.core.plugins import combiner
from insights.combiners.hostname import hostname
from insights.parsers.lssap import Lssap


@combiner(hostname, Lssap)
class Sap(object):
    """
    Combiner for analyzing the SAP instances running on the system.

    Examples:
        >>> type(saps)
        <class 'insights.combiners.sap.Sap'>
        >>> saps.is_hana
        True
        >>> saps.is_netweaver
        True
        >>> saps.is_ascs
        False
    """
    sap_type = {'D': 'netweaver',
                'HDB': 'hana',
                'ASCS': 'ascs'}

    def __init__(self, hostname, sap):
        hn = hostname.hostname
        # Rule only matters if the SAP instance returned by lssap refers to this
        # host
        instances = [i['Instance'] for i in sap.data if hn == i['SAPLOCALHOST']]
        sap_apps = []
        for i in instances:
            sap_apps.extend([v
                for k, v in self.sap_type.items()
                if i.startswith(k)])
        self._sap_apps = list(set(sap_apps))

    @property
    def running_saps(self):
        """list: List SAP instances running on the system."""
        return self._sap_apps

    @property
    def is_netweaver(self):
        """bool: SAP Netweaver is running on the system."""
        return 'netweaver' in self._sap_apps

    @property
    def is_hana(self):
        """bool: SAP Hana is running on the system."""
        return 'hana' in self._sap_apps

    @property
    def is_ascs(self):
        """bool: SAP System Central Services is running on the system."""
        return 'ascs' in self._sap_apps
