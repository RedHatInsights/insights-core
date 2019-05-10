"""
NetSysconfig -file ``/etc/sysconfig/network``
---------------------------------------------
"""

from insights import parser, SysconfigOptions
from insights.specs import Specs


@parser(Specs.sysconfig_network)
class NetSysconfig(SysconfigOptions):
    """
    This parser parses the ``/etc/sysconfig/network`` configuration file

    Sample Input::

        NETWORKING=yes
        HOSTNAME=rhel7-box
        GATEWAY=172.31.0.1
        NM_BOND_VLAN_ENABLED=no

    Examples:

        >>> 'NETWORKING' in net_syscfg
        True
        >>> net_syscfg['GATEWAY']
        '172.31.0.1'
    """
    pass
