"""
Microsoft SQL Server Database Engine configuration - file ``/var/opt/mssql/mssql.conf``
=======================================================================================
"""
from insights.core import IniConfigFile
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.mssql_conf)
class MsSQLConf(IniConfigFile):
    """
    The Microsoft SQL Server configuration file is a standard '.ini' file and uses
    the ``IniConfigfile`` class to read it.

    Sample configuration::

        [sqlagent]
        enabled = false

        [EULA]
        accepteula = Y

        [memory]
        memorylimitmb = 3328

    Examples:
        >>> type(conf)
        <class 'insights.parsers.mssql_conf.MsSQLConf'>
        >>> conf.has_option('memory', 'memorylimitmb')
        True
        >>> conf.get('memory', 'memorylimitmb') == '3328'
        True
    """
    pass
