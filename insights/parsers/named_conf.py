"""
NamedConf parser - file ``/etc/named.conf``
===========================================

NamedConf parser the file named configuration file.
Named is a name server used by BIND.
"""

import re

from insights.core.plugins import parser
from insights.parsers import SkipException
from insights.specs import Specs
from insights.parsers.named_checkconf import NamedCheckconf

# regex for matching 'include' section
INCLUDE_FILES = re.compile(r'include.*;')


@parser(Specs.named_conf)
class NamedConf(NamedCheckconf):
    """
    Class for parsing the file ``/etc/named.conf```

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

        try:
            super(NamedConf, self).parse_content(content)
        except SkipException as e:
            raise e

        for include_entry in INCLUDE_FILES.finditer('\n'.join(content)):
            self.includes.append(include_entry.group(0).replace('"', '').replace(';', '').split()[-1])
