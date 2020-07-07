"""
SSSDNetworkConfig - file ``/etc/systemd/system/sssd.service.d/network.conf``
============================================================================

The SSSDNetworkConfig configuration file is a standard '.ini' file and this parser uses
the ``IniConfigFile`` class to read it.
"""

from .. import IniConfigFile, parser
from insights.specs import Specs


@parser(Specs.sssd_network_config)
class SSSDNetworkConfig(IniConfigFile):
    """
    Parse the content of the ``/etc/systemd/system/sssd.service.d/network.conf`` file.

    Sample input for ``/etc/systemd/system/sssd.service.d/network.conf``::

        [Unit]
        Before=systemd-user-sessions.service nss-user-lookup.target
        After=network-online.target
        Wants=nss-user-lookup.target

    Examples:
        >>> type(sssd_network_config_obj)
        <class 'insights.parsers.sssd_network_config.SSSDNetworkConfig'>
        >>> sssd_network_config_obj.get('Unit', 'Before') == 'systemd-user-sessions.service nss-user-lookup.target'
        True
        >>> sssd_network_config_obj.get('Unit', 'After') == 'network-online.target'
        True
        >>> sssd_network_config_obj.get('Unit', 'Wants') == 'nss-user-lookup.target'
        True
    """
    pass
