"""
TunedConfIni - file ``/etc/tuned.conf``
=======================================
"""

from insights import Parser, parser, get_active_lines
from insights.specs import Specs
from insights.contrib.ConfigParser import NoSectionError, NoOptionError


@parser(Specs.tuned_conf)
class TunedConfIni(Parser):
    """This class parses the ``/etc/tuned.conf`` file using the
    ``IniConfigFile`` base parser.

    Sample configuration file::

        #
        # Net tuning section
        #
        [NetTuning]
        # Enabled or disable the plugin. Default is True. Any other value
        # disables it.
        enabled=False

        #
        # CPU monitoring section
        #
        [CPUMonitor]
        # Enabled or disable the plugin. Default is True. Any other value
        # disables it.
        # enabled=False


    Examples:
        >>> 'NetTuning' in tuned_obj.sections
        True
        >>> tuned_obj.get('NetTuning', 'enabled') == "False"
        True
        >>> tuned_obj.getboolean('NetTuning', 'enabled') == False
        True
        >>> sorted(tuned_obj.sections)
        ['CPUMonitor', 'NetTuning']
    """

    _boolean_states = {'true': True, 'false': False}

    def parse_content(self, content):
        self.data = {}
        self._sections = []
        for line in get_active_lines(content):
            if line.startswith('['):
                _section = line.split(']')[0].strip("[")
                self._sections.append(_section)
                self.data[_section] = {}
            else:
                key, val = line.split('=')
                self.data[_section][key] = val

    @property
    def sections(self):
        """
        (list): Returns a list of **sections** present in the file
        """
        return self._sections

    def get(self, section, opt):
        """
        get(section, option)
        (str): Returns a string value for the named **section** and
            corresponding **option**.
        """
        if section and section not in self._sections:
            raise NoSectionError(section)
        elif opt not in self.data[section]:
            raise NoOptionError(opt, section)
        elif self.data[section][opt]:
            return self.data[section][opt]
        else:
            return None

    def getboolean(self, section, option):
        """
        getboolean(section, options)
        (bool): like get(), but it will convert value to a boolean
        """
        v = self.get(section, option)
        if v.lower() not in self._boolean_states:
            raise ValueError('Not a boolean: %s' % v)
        return self._boolean_states[v.lower()]
