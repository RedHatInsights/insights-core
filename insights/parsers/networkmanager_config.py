"""
NetworkManagerConfig - file ``/etc/NetworkManager/NetworkManager.conf``
=======================================================================
"""
from insights.core import IniConfigFile
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.networkmanager_conf)
class NetworkManagerConfig(IniConfigFile):
    """
    The ``/etc/NetworkManager/NetworkManager.conf`` file is in a standard '.ini' format,
    and this parser uses the IniConfigFile base class to read this.

    Given a file containing the following test data::

        [main]
        dhcp=dhclient

    Example:
        >>> type(networkmanager_config_obj)
        <class 'insights.parsers.networkmanager_config.NetworkManagerConfig'>
        >>> networkmanager_config_obj.get('main', 'dhcp') == 'dhclient'
        True
    """
    pass
