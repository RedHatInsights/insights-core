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
GetconfPageSize - command ``/usr/sbin/getconf PAGE_SIZE``
=========================================================

This very simple parser returns the output of the ``getconf PAGE_SIZE`` command.

Examples:

    >>> pagesize_parsed.page_size
    4096
"""
from . import ParseException
from .. import parser, CommandParser
from insights.specs import Specs


@parser(Specs.getconf_page_size)
class GetconfPageSize(CommandParser):
    """Class for parsing 'getconf PAGE_SIZE' command output

    Output: page_size

    Attributes:
        page_size (int): returns the page_size in bytes depending upon the architecture
    """

    def parse_content(self, content):
        if len(content) != 1:
            msg = "getconf PAGE_SIZE output contains multiple non-empty lines"
            raise ParseException(msg)
        raw = content[0].strip()
        self.page_size = int(raw)

    def __str__(self, context):
        return "<page_size: {}>".format(self.page_size)
