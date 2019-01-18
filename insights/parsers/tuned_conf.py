"""
TunedConfIni - file ``/etc/tuned.conf``
=======================================
"""

import io
from insights import IniConfigFile, parser, get_active_lines
from insights.specs import Specs
from insights.contrib.ConfigParser import RawConfigParser


@parser(Specs.tuned_conf)
class TunedConfIni(IniConfigFile):
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
        >>> 'NetTuning' in tuned_obj.sections()
        True
        >>> tuned_obj.get('NetTuning', 'enabled') == "False"
        True
        >>> tuned_obj.getboolean('NetTuning', 'enabled') == False
        True
        >>> sorted(tuned_obj.sections())
        ['CPUMonitor', 'NetTuning']
    """

    def parse_content(self, content, allow_no_value=False):
        content = get_active_lines(content)

        super(IniConfigFile, self).parse_content(content)
        config = RawConfigParser(allow_no_value=allow_no_value)
        fp = io.StringIO(u"\n".join(content))
        config.readfp(fp, filename=self.file_name)
        self.data = config
    pass
