"""
TunedConfIni - file ``/etc/tuned.conf``
=======================================
"""

from insights.core import IniConfigFile
from insights.core.plugins import parser
from insights.specs import Specs


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
        >>> sorted(tuned_obj.sections())==sorted(['CPUMonitor', 'NetTuning'])
        True
    """
    def parse_content(self, content, allow_no_value=True):
        super(TunedConfIni, self).parse_content(content, allow_no_value)
