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

from .. import parser, get_active_lines, Parser
import re
from insights.specs import Specs


@parser(Specs.scheduler)
class Scheduler(Parser):

    def parse_content(self, content):
        active_scheduler_regex = re.compile(r'\[.*]')
        result = {}
        for line in get_active_lines(content):
            for sched in line.split():
                active_scheduler = active_scheduler_regex.search(sched)
                if active_scheduler:
                    result[self.file_path.split('/')[3]] = active_scheduler.group()
        self.data = result
