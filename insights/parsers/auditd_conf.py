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
AuditdConf - file ``/etc/audit/auditd.conf``
============================================

The auditd.conf file is a standard key = value file with hash comments.
Active settings are provided using the `get_active_settings_value` method or
by using the dictionary `contains` functionality.

Example:

    >>> conf = shared[AuditdConf]
    >>> conf.get_active_setting_value('log_group')
    'root'
    >>> 'log_file' in conf
    True
"""

from .. import Parser, parser, get_active_lines
from ..parsers import split_kv_pairs
from insights.specs import Specs


@parser(Specs.auditd_conf)
class AuditdConf(Parser):
    """
    A parser for accessing /etc/audit/auditd.conf.
    """

    def __init__(self, *args, **kwargs):
        self.active_lines_unparsed = []
        self.active_settings = {}
        super(AuditdConf, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        """
        Main parsing class method which stores all interesting data from the content.

        Args:
            content (context.content): Parser context content
        """
        self.active_lines_unparsed = get_active_lines(content)
        #  (man page specifies that a line must contain "=")
        self.active_settings = split_kv_pairs(content, use_partition=False)

    def get_active_setting_value(self, setting_name):
        """
        Access active setting value by setting name.

        Args:
            setting_name (string): Setting name
        """
        return self.active_settings[setting_name]
