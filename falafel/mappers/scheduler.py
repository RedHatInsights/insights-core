from .. import mapper, get_active_lines, Mapper
import re


@mapper('scheduler')
class Scheduler(Mapper):

    def parse_content(self, content):
        active_scheduler_regex = re.compile(r'\[.*]')
        result = {}
        for line in get_active_lines(content):
            for scheduler in line.split():
                active_scheduler = active_scheduler_regex.search(scheduler)
                if active_scheduler:
                    result[self.file_path.split('/')[3]] = active_scheduler.group()
        self.data = result
