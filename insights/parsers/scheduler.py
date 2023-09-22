"""
Scheduler - file ``/sys/block/*/queue/scheduler``
=================================================

This parser parses the content from scheduler files. It stores available
values and also current selection for every device.

Sample content from schduler file:

    noop deadline [cfq]

Examples:
    >>> type(scheduler_obj)
    <class 'insights.parsers.scheduler.Scheduler'>
    >>> scheduler_obj.data
    {'sda': '[cfq]'}
    >>> scheduler_obj.device
    'sda'
    >>> scheduler_obj.schedulers
    ['noop', 'deadline', 'cfq']
    >>> scheduler_obj.active_scheduler
    'cfq'

"""

import re

from insights.specs import Specs
from .. import parser, get_active_lines, Parser


@parser(Specs.scheduler)
class Scheduler(Parser):
    """
    This class provides parsing for content of ``/sys/block/*/queue/scheduler``
    files.

    Attributes:
        device (str): Block device name
        schedulers (list): A list of available schedulers
        active_scheduler (str): An active scheduler
        data (dict): A dictionary with block device name as a key and an active scheduler as
            a value.
    """
    ACTIVE_SCHEDULER_PATTERN = re.compile(r'\[(.*)]')

    def parse_content(self, content):
        self.device = None
        self.schedulers = []
        self.active_scheduler = None
        self.data = {}  # Legacy value to keep backwards compatibility

        self.device = self.file_path.split('/')[3]
        for line in get_active_lines(content):
            r = self.ACTIVE_SCHEDULER_PATTERN.search(line)
            if r:
                self.active_scheduler = r.group(1)

            self.schedulers = line.replace('[', '').replace(']', '').split()

        # Set legacy values
        if self.active_scheduler:
            self.data = {self.device: '[' + self.active_scheduler + ']'}
