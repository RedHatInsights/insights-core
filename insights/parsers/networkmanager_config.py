"""
NetworkManagerConfig - file ``/etc/NetworkManager/NetworkManager.conf``
=======================================================================

The ``/etc/NetworkManager/NetworkManager.conf`` file is in a standard '.ini' format,
and this parser uses the IniConfigFile base class to read this.

Given a file containing the following test data::

    [main]
    #plugins=ifcfg-rh,ibft
    dhcp=dhclient

Example:
    >>> type(networkmanager_config_obj)
    <class 'insights.parsers.networkmanager_config.NetworkManagerConfig'>
    >>> networkmanager_config_obj.get('main', 'dhcp') == 'dhclient'
    True
"""

from .. import parser, IniConfigFile
from insights.specs import Specs


@parser(Specs.networkmanager_conf)
class NetworkManagerConfig(IniConfigFile):
    """
    A dict of the content of the ``NetworkManager.conf`` configuration file.

    Example selection of dictionary contents::

        {
            'main': {
                'dhcp':'dhclient',
             }
        }
    """
    pass
