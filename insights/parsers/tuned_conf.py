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
TunedConfIni - file ``/etc/tuned.conf``
=======================================
"""

from insights import IniConfigFile, parser, get_active_lines
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
        content = get_active_lines(content)
        super(TunedConfIni, self).parse_content(content, allow_no_value)
