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

from .. import Parser, parser, LegacyItemAccess
from insights.specs import Specs


@parser(Specs.ovirt_engine_confd)
class OvirtEngineConfd(LegacyItemAccess, Parser):

    def parse_content(self, content):
        self.data = dict((k.strip('" '), v.strip('" '))
                         for k, _, v in [l.partition("=") for l in content])
