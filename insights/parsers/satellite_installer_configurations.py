"""
Satellite installer configuration files
=======================================

Parsers included in this module are:

CustomHiera - file ``/etc/foreman-installer/custom-hiera.yaml``
---------------------------------------------------------------
Parsers the file `/etc/foreman-installer/custom-hiera.yaml`

"""
import sys
import six

from insights import parser, YAMLParser
from insights.specs import Specs
from insights.parsers import SkipException, ParseException


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
        self.is_invalid_yaml = False
        try:
            super(CustomHiera, self).parse_content(content)
        except SkipException:
            pass
        except ParseException as ex:
            if "couldn't parse yaml" in str(ex):
                self.is_invalid_yaml = True
            else:
                six.reraise(*sys.exc_info())
