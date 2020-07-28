"""
NamedConf parser - file ``/etc/named.conf``
===========================================

NamedConf parser the file named configuration file.
Named is a name server used by BIND.
"""

import re

from insights.specs import Specs
from insights.core.plugins import parser
from insights.parsers.named_checkconf import NamedCheckconf

# regex for matching 'include' section
INCLUDE_FILES = re.compile(r'include.*;')


@parser(Specs.named_conf)
class NamedConf(NamedCheckconf):
    """
    Class for parsing the file ``/etc/named.conf```, We use class ``NamedCheckConf`` to parse most
    of the named.conf configurations and class ``NamedConf`` to parse the `include` directives.

    .. note::
        Please refer to the super-class :py:class:`insights.parsers.named_checkconf:NamedCheckConf`
        for more usage information.

    Attributes:
        includes (list): List of files in 'include' section.

    Raises:
        SkipException: When content is empty or cannot be parsed.

    Examples:
        >>> named_conf.includes
        ['/etc/crypto-policies/back-ends/bind.config']
    """

    def parse_content(self, content):
        self.includes = []

        super(NamedConf, self).parse_content(content)

        for include_entry in INCLUDE_FILES.finditer('\n'.join(content)):
            self.includes.append(include_entry.group(0).replace('"', '').replace(';', '').split()[-1])
