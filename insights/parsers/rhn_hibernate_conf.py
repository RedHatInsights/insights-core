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


@parser(Specs.rhn_hibernate_conf)
class RHNHibernateConf(LegacyItemAccess, Parser):

    def parse_content(self, content):
        """
        Parses rhn_hibernate.conf and returns a dict.
        - {
            "hibernate.c3p0.min_size": '5'
            "hibernate.c3p0.preferredTestQuery": "select 'c3p0 ping' from dual"
          }
        """
        hb_dict = {}
        for line in get_active_lines(content):
            if '=' in line:
                key, _, value = line.partition('=')
                hb_dict[key.strip()] = value.strip()
        self.data = hb_dict
