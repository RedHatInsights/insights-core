"""
pluginconf.d configuration file - Files
=======================================

Shared mappers for parsing and extracting data from
``/etc/yum/pluginconf.d/*.conf`` files. Parsers contained
in this module are:

PluginConfD - files ``/etc/yum/pluginconf.d/*.conf``
---------------------------------------------------

PluginConfDIni - files ``/etc/yum/pluginconf.d/*.conf``
-------------------------------------------------------
"""
from insights.core import IniConfigFile, LegacyItemAccess, Parser
from insights.core.plugins import parser
from insights.parsers import get_active_lines
from insights.specs import Specs
from insights.util import deprecated


@parser(Specs.pluginconf_d)
class PluginConfD(LegacyItemAccess, Parser):
    """
    .. warning::
        This parser is deprecated, please use
        :py:class:`insights.parsers.pluginconf_d.PluginConfDIni` instead

    Class to parse configuration file under ``pluginconf.d``

    Sample configuration::

        [main]
        enabled = 0
        gpgcheck = 1
        timeout = 120

        # You can specify options per channel, e.g.:
        #
        #[rhel-i386-server-5]
        #enabled = 1
        #
        #[some-unsigned-custom-channel]
        #gpgcheck = 0
    """
    def parse_content(self, content):
        deprecated(PluginConfD, "Deprecated. Use 'PluginConfDIni' instead.")
        plugin_dict = {}
        section_dict = {}
        key = None
        for line in get_active_lines(content):
            if line.startswith('['):
                section_dict = {}
                plugin_dict[line[1:-1]] = section_dict
            elif '=' in line:
                key, _, value = line.partition("=")
                key = key.strip()
                section_dict[key] = value.strip()
            else:
                if key:
                    section_dict[key] = ','.join([section_dict[key], line])
        self.data = plugin_dict

    def __iter__(self):
        for sec in self.data:
            yield sec


@parser(Specs.pluginconf_d)
class PluginConfDIni(IniConfigFile):
    """
    Read yum plugin config files, in INI format, using the standard INI file
    parser class.

    Sample configuration::

        [main]
        enabled = 0
        gpgcheck = 1
        timeout = 120

        # You can specify options per channel, e.g.:
        #
        #[rhel-i386-server-5]
        #enabled = 1
        #
        #[some-unsigned-custom-channel]
        #gpgcheck = 0

        [test]
        test_multiline_config = http://example.com/repos/test/
                                http://mirror_example.com/repos/test/

    Examples:
        >>> type(conf)
        <class 'insights.parsers.pluginconf_d.PluginConfDIni'>
        >>> conf.sections()
        ['main', 'test']
        >>> conf.has_option('main', 'gpgcheck')
        True
        >>> conf.get("main", "enabled")
        '0'
        >>> conf.getint("main", "timeout")
        120
        >>> conf.getboolean("main", "enabled")
        False
        >>> conf.get("test", "test_multiline_config")
        'http://example.com/repos/test/ http://mirror_example.com/repos/test/'
    """
    pass
