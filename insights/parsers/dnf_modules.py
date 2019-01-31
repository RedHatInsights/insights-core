"""
DnfModules - files under in the ``/etc/dnf/modules.d/`` directory
=================================================================

Modularity configuration
"""
from insights import IniConfigFile, parser
from insights.specs import Specs


@parser(Specs.dnf_modules)
class DnfModules(IniConfigFile):
    """
    Provides access to state of enabled modules/streams/profiles
    which is located in the /etc/dnf/modules.d/ directory

    Examples:
        >>> len(dnf_modules.sections())
        3
        >>> str(dnf_modules.get("postgresql", "stream"))
        '9.6'
        >>> str(dnf_modules.get("postgresql", "profiles"))
        'client'
    """
    pass
