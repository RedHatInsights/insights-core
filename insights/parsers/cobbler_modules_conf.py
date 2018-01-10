"""
Cobbler modules configuration - file ``/etc/cobbler/modules.conf``
==================================================================

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

    >>> conf = CobblerModulesConf(context_wrap(conf_content))
    >>> conf.get('authentication', 'module')
    'authn_spacewalk'
    >>> conf.get('dhcp', 'module')
    'manage_isc'

"""

from .. import parser, IniConfigFile
from insights.specs import Specs


@parser(Specs.cobbler_modules_conf)
class CobblerModulesConf(IniConfigFile):
    """
    This uses the standard ``IniConfigFile`` parser class.
    """
    pass
