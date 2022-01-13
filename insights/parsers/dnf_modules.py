"""
DnfModules - files under in the ``/etc/dnf/modules.d/`` directory
=================================================================
"""
from insights.core import IniConfigFile
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.dnf_modules)
class DnfModules(IniConfigFile):
    """
    Provides access to state of enabled modules/streams/profiles
    which is located in the /etc/dnf/modules.d/ directory

    Examples:
        >>> type(dnf_modules)
        <class 'insights.parsers.dnf_modules.DnfModules'>
        >>> len(dnf_modules.sections())
        3
        >>> str(dnf_modules.get("postgresql", "stream"))
        '9.6'
        >>> str(dnf_modules.get("postgresql", "profiles"))
        'client'
    """
    pass
