"""
VmwareToolsConf - file ``/etc/vmware-tools/tools.conf``
=======================================================
This parser is used to parse the content of file ``/etc/vmware-tools/tools.conf``.
"""

from insights.core import IniConfigFile
from insights.core.filters import add_filter
from insights.core.plugins import parser
from insights.specs import Specs

add_filter(Specs.vmware_tools_conf, ["["])


@parser(Specs.vmware_tools_conf)
class VmwareToolsConf(IniConfigFile):
    """
    Parse the ``/etc/vmware-tools/tools.conf`` configuration file.

    Sample configuration::

         [servicediscovery]
         disabled=false

         [gueststoreupgrade]
         poll-interval=3600

    Examples:
        >>> type(vmware_tools_conf_parser)
        <class 'insights.parsers.vmware_tools_conf.VmwareToolsConf'>
        >>> vmware_tools_conf_parser.has_option("servicediscovery", "disabled")
        True
        >>> vmware_tools_conf_parser.get("servicediscovery", "disabled") == "false"
        True
    """
    pass
