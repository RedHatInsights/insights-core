"""
NamedConf parser - file ``/etc/named.conf``
===========================================

NamedConf parser the file named configuration file.
Named is a name server used by BIND.
"""

from insights.specs import Specs
from insights.core.plugins import parser
from insights.parsers import SkipException
from insights.parsers.named_checkconf import NamedCheckconf


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
        includes = []
        super(NamedConf, self).parse_content(content)

        try:
            for line in [l for l in content if l.strip().startswith('include ') and ';' in l]:
                includes.append(line.split(';')[0].replace('"', '').split()[1])
        except IndexError:
            raise SkipException("Syntax error of include directive")

        self.includes = includes
