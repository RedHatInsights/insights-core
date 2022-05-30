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
    of the named.conf configurations and class ``NamedConf`` to parse the `include` directives and
    the `allow-recursion` value from the `options` section.

    .. note::
        Please refer to the super-class :py:class:`insights.parsers.named_checkconf:NamedCheckConf`
        for more usage information.

    Attributes:
        includes (list): List of files in 'include' and 'allow-recursion' value from the 'options' section.

    Raises:
        SkipException: When content is empty or cannot be parsed.

    Examples:
        >>> named_conf.includes
        ['/etc/crypto-policies/back-ends/bind.config']
        >>> named_conf.allow_recursion_address
        ['localnets', 'localhost', '192.168.10.1/24']
    """

    def parse_content(self, content):
        includes = []
        allow_recursion_address = []
        options_flag = False
        super(NamedConf, self).parse_content(content)

        try:
            for line in content:
                if line.strip().startswith('include ') and ';' in line:
                    includes.append(line.split(';')[0].replace('"', '').split()[1])
                if line.strip().startswith('options ') and ';' not in line:
                    options_flag = True
                if options_flag and line.strip().startswith('allow-recursion ') and line.endswith(';'):
                    for addr in line.strip().split('allow-recursion', 1)[1].split('{', 1)[1].split('}', 1)[0].split():
                        allow_recursion_address.append(addr.split(';', 1)[0])

        except IndexError:
            raise SkipException("Syntax error of include directive")

        self.includes = includes
        self.allow_recursion_address = allow_recursion_address
