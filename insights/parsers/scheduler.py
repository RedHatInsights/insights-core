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
