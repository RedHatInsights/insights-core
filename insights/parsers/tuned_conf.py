"""
This module contains following parser:

TunedConfIni - file ``/etc/tuned.conf``
------------------------------------
"""

from .. import IniConfigFile, parser
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
        >>> 'NetTuning' in tuned_obj
        True
        >>> tuned_obj.get('NetTuning', 'enabled') == "False"
        True
        >>> tuned_obj.getboolean('NetTuning', 'enabled') == False
        True
    """
    pass
