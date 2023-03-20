"""
Cobbler modules configuration - file ``/etc/cobbler/modules.conf``
==================================================================
"""
from insights.core import IniConfigFile
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.cobbler_modules_conf)
class CobblerModulesConf(IniConfigFile):
    """
    The Cobbler modules configuration lists a set of services, and typically
    sets the module that provides that service.

    Sample input::

        [authentication]
        module = authn_spacewalk

        [authorization]
        module = authz_allowall

        [dns]
        module = manage_bind

        [dhcp]
        module = manage_isc

    Examples:

        >>> type(conf)
        <class 'insights.parsers.cobbler_modules_conf.CobblerModulesConf'>
        >>> conf.get('authentication', 'module')
        'authn_spacewalk'
        >>> conf.get('dhcp', 'module')
        'manage_isc'
    """
    pass
