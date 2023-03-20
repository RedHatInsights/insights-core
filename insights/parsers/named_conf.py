"""
NamedConf parser - file ``/etc/named.conf``
===========================================

NamedConf parser the file named configuration file.
Named is a name server used by BIND.
"""
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.parsers.named_checkconf import NamedCheckconf
from insights.specs import Specs


@parser(Specs.named_conf)
class NamedConf(NamedCheckconf):
    """
    Class for parsing the file ``/etc/named.conf```, We use class ``NamedCheckConf`` to parse most
    of the named.conf configurations and class ``NamedConf`` to parse the `include` directives and
    the `allow-recursion` values.

    .. note::
        Please refer to the super-class :py:class:`insights.parsers.named_checkconf:NamedCheckConf`
        for more usage information.

    Attributes:
        includes (list): List of files in 'include' section.
        allow_recursion_address (list): List of address in 'allow-recursion' section.

    Raises:
        SkipComponent: When content is empty or cannot be parsed.

    Examples:
        >>> named_conf.includes
        ['/etc/crypto-policies/back-ends/bind.config']
        >>> named_conf.allow_recursion_address
        ['localnets', 'localhost', '192.168.10.1/24']
    """

    def parse_content(self, content):
        includes = []
        allow_recursion_address = []
        super(NamedConf, self).parse_content(content)

        try:
            for line in content:
                line = line.strip()
                if line.startswith('include ') and ';' in line:
                    includes.append(line.split(';')[0].replace('"', '').split()[1])
                if line.startswith('allow-recursion ') and line.endswith(';'):
                    allow_recursion_address.extend(i.strip(';') for i in line.split(None, 1)[1].strip('{}; ').split())

        except IndexError:
            raise SkipComponent("Syntax error of include directive")

        self.includes = includes
        self.allow_recursion_address = allow_recursion_address
