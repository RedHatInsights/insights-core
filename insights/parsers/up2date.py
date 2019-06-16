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

from .. import Parser, parser, get_active_lines, LegacyItemAccess
from insights.specs import Specs
from insights.util import deprecated


@parser(Specs.up2date)
class Up2Date(LegacyItemAccess, Parser):
    """
    .. warning::
        This parser is deprecated, please use
        :py:class:`insights.parsers.sysconfig.Up2DateSysconfig` instead.

    Class to parse the ``up2date``

    Attributes:
        data (dict): A dict of up2date info which ignores comment lines.
        The first and second line for key word 'serverURL' will be ignored.

    For example:
        serverURL[comment]=Remote server URL
        #serverURL=https://rhnproxy.glb.tech.markit.partners/XMLRPC
        serverURL=https://rhnproxy.glb.tech.markit.partners/XMLRPC
    """
    def __init__(self, *args, **kwargs):
        deprecated(Up2Date, "Import Up2DateSysconfig from insights.parsers.sysconfig instead")
        super(Up2Date, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        up2date_info = {}
        for line in get_active_lines(content):
            if "[comment]" not in line and '=' in line:
                key, val = line.split('=')
                up2date_info[key.strip()] = val.strip()
        self.data = up2date_info
