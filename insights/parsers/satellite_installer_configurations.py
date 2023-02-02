"""
Satellite installer configuration files
=======================================

Parsers included in this module are:

CustomHiera - file ``/etc/foreman-installer/custom-hiera.yaml``
---------------------------------------------------------------
Parsers the file `/etc/foreman-installer/custom-hiera.yaml`

"""
from insights.core import YAMLParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
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
    def parse_content(self, content):
        try:
            super(CustomHiera, self).parse_content(content)
        except SkipComponent:
            pass
