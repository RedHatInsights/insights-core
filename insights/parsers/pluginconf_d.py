"""
pluginconf.d configuration file - Files
=======================================

Shared mappers for parsing and extracting data from
``/etc/yum/pluginconf.d/*.conf`` files. Parsers contained
in this module are:

PluginConfDIni - files ``/etc/yum/pluginconf.d/*.conf``
-------------------------------------------------------
"""
from insights.core import IniConfigFile
from insights.core.plugins import parser
from insights.specs import Specs


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
