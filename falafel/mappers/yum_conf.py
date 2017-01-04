from ConfigParser import NoOptionError
from .. import mapper, IniConfigFile



@mapper('yum.conf')
class YumConf(IniConfigFile):
    """Class to parse the ``/etc/yum.conf`` file"""
    def parse_content(self, content):
        super(YumConf, self).parse_content(content)
        # File /etc/yum.conf may contain repos definitions.
        # Keywords 'gpgkey' and 'baseurl' might contain multiple values separated by comma.
        # Convert those values into a list.
        for section in self.sections():
            for key in ('gpgkey', 'baseurl'):
                try:
                    value = self.get(section, key)
                    if value and isinstance(value, str):
                        self.data.set(section, key, value.split(','))
                except NoOptionError:
                    pass
