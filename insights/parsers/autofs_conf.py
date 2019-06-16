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
AutoFSConf - file ``/etc/autofs.conf``
======================================

The `/etc/autofs.conf` file is in a standard '.ini' format, and this parser
uses the IniConfigFile base class to read this.

Example:
    >>> config = shared[AutoFSConf]
    >>> config.sections()
    ['autofs', 'amd']
    >>> config.items('autofs')
    ['timeout', 'browse_mode', 'mount_nfs_default_protocol']
    >>> config.has_option('amd', 'map_type')
    True
    >>> config.get('amd', 'map_type')
    'file'
    >>> config.getint('autofs', 'timeout')
    300
    >>> config.getboolean('autofs', 'browse_mode')
    False
"""

from .. import parser, IniConfigFile
from insights.specs import Specs


@parser(Specs.autofs_conf)
class AutoFSConf(IniConfigFile):
    """
        /etc/autofs.conf is a standard INI style config file.
    """
    pass
