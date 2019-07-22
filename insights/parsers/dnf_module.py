"""
dnf module commands
===================

Parsers provided in this module includes:

DnfModuleList - command ``dnf module list``
-------------------------------------------

DnfModuleInfo - command ``dnf module info *``
---------------------------------------------
"""
from insights import parser
from insights.core import CommandParser
#, DictToAttribute
from insights.parsers import parse_fixed_table, SkipException
from insights.specs import Specs


class DictToAttribute(object):
    """
    Class to access the items in dict via attribute.  The original access method
    of dict is also remained.  The desired attributes must be defined in the
    ``self.attrs`` explicitly.
     Attributes:
        attrs (dict): Attributes and the default values need to be set for the
            class.
     Raises:
        NotImplementedError: When no attributes are defined.
    """
    attrs = {}

    def __init__(self, data={}):
        if not self.attrs:
            raise NotImplementedError('Attributes must be defined in "self.attrs" explicitly.')
        for k, v in self.attrs.items():
            setattr(self, k, v) if k not in data else None
        for k, v in data.items():
            setattr(self, k, v)
        self._keys = sorted(data.keys())

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def __contains__(self, item):
        return item in self._keys

    def get(self, item, default=None):
        return self.__getattribute__(item) if item in self._keys else default

    def items(self):
        for k in self._keys:
            yield k, self.__getattribute__(k)


class DnfModule(DictToAttribute):
    """
    An object for modules listed by ``dnf module list``

    Attributes:
        'name' (str): Name of the dnf module
        'stream' (str): Stream of the dnf module
        'profiles' (str): Profiles of the dnf module
        'summary' (str): Summary of the dnf module
    """
    attrs = {
            'name': '',
            'stream': '',
            'profiles': '',
            'summary': '',
    }

    def __init__(self, data={}):
        super(DnfModule, self).__init__(data)
        self.keys = self._keys


@parser(Specs.dnf_module_list)
class DnfModuleList(CommandParser, dict):
    """
    Examples:
        >>> len(dnf_modules.sections())
        3
        >>> str(dnf_modules.get("postgresql", "stream"))
        '9.6'
        >>> str(dnf_modules.get("postgresql", "profiles"))
        'client'
    """

    def parse_content(self, content):
        data = parse_fixed_table(content,
                        heading_ignore=['Name', 'Stream', 'Profiles', 'Summary'],
                        trailing_ignore=['Hint:'])
        if not data:
            raise SkipException('Nothing need to parse.')
        self.update({l['Name']: DnfModule({k.lower(): v for k, v in l.items()}) for l in data})
