"""
Satellite installer configuration files
=======================================

Parsers included in this module are:

CustomHiera - file ``/etc/foreman-installer/custom-hiera.yaml``
---------------------------------------------------------------
Parsers the file `/etc/foreman-installer/custom-hiera.yaml`

"""

from insights import parser, YAMLParser
from insights.specs import Specs


@parser(Specs.satellite_custom_hiera)
class CustomHiera(YAMLParser):
    """
    Class to parse ``/etc/foreman-installer/custom-hiera.yaml``

    Examples:
        >>> 'apache::mod::prefork::serverlimit' in custom_hiera
        True
        >>> custom_hiera['apache::mod::prefork::serverlimit']
        582
    """

    pass
