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
AvcCacheThreshold - File ``/sys/fs/selinux/avc/cache_threshold``
================================================================

This parser reads the content of ``/sys/fs/selinux/avc/cache_threshold``.
"""

from .. import parser, CommandParser

from ..parsers import ParseException
from insights.specs import Specs


@parser(Specs.avc_cache_threshold)
class AvcCacheThreshold(CommandParser):
    """
    Class ``AvcCacheThreshold`` parses the content of the ``/sys/fs/selinux/avc/cache_threshold``.

    Attributes:
        cache_threshold (int): It is used to show the value of cache threshold.

    A typical sample of the content of this file looks like::

        512

    Examples:
        >>> type(avc_cache_threshold)
        <class 'insights.parsers.avc_cache_threshold.AvcCacheThreshold'>
        >>> avc_cache_threshold.cache_threshold
        512
    """

    def parse_content(self, content):
        if len(content) != 1:
            raise ParseException("Error: ", content[0] if content else 'empty file')
        self.cache_threshold = int(content[0].strip())
