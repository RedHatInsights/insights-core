"""
Microsoft SQL Server Database Engine configuration - file ``/var/opt/mssql/mssql.conf``
=======================================================================================

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

    >>> conf.has_option('memory', 'memorylimitmb')
    True
    >>> conf.get('memory', 'memorylimitmb') == '3328'
    True
"""
from insights.specs import Specs
from .. import parser, IniConfigFile


@parser(Specs.mssql_conf)
class MsSQLConf(IniConfigFile):
    """Microsoft SQL Server Database Engine configuration parser class, based on
    the ``IniConfigFile`` class.
    """
    pass
