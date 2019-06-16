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

from .. import Parser, parser, get_active_lines, LegacyItemAccess, IniConfigFile
from insights.specs import Specs


@parser(Specs.pluginconf_d)
class PluginConfD(LegacyItemAccess, Parser):
    """Class to parse configuration file under ``pluginconf.d``

    Attributes:
        data (dict): A dict likes
            {
                "main": {
                    "gpgcheck": "1",
                    "enabled": "0",
                    "timeout": "120"
                }
            }
    """

    def parse_content(self, content):
        """
        ---Sample---
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
    """
    pass
