#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
