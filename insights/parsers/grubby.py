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
grubby - command ``/usr/sbin/grubby``
=====================================

This is a collection of parsers that all deal with the command ``grubby``.
Parsers included in this module are:

GrubbyDefaultIndex - command ``grubby --default-index``
-------------------------------------------------------

GrubbyDefaultKernel - command ``grubby --default-kernel``
---------------------------------------------------------
"""

from insights.specs import Specs
from insights.parsers import SkipException, ParseException
from insights import CommandParser
from insights import parser


@parser(Specs.grubby_default_index)
class GrubbyDefaultIndex(CommandParser):
    """
    This parser parses the output of command ``grubby --default-index``.

    The typical output of this command is::

        0

    Examples:
        >>> grubby_default_index.default_index
        0

    Raises:
        SkipException: When output is empty
        ParseException: When output is invalid

    Attributes:
        default_index (int): the numeric index of the current default boot entry, count from 0
    """
    def parse_content(self, content):
        if not content:
            raise SkipException('Empty output')
        if len(content) != 1 or not content[0].isdigit():
            raise ParseException('Invalid output: {0}', content)
        self.default_index = int(content[0])


@parser(Specs.grubby_default_kernel)
class GrubbyDefaultKernel(CommandParser):
    """
    This parser parses the output of command ``grubby --default-kernel``.

    The typical output of this command is::

        /boot/vmlinuz-2.6.32-573.el6.x86_64

    Examples:

        >>> grubby_default_kernel.default_kernel
        '/boot/vmlinuz-2.6.32-573.el6.x86_64'

    Raises:
        SkipException: When output is empty
        ParseException: When output is invalid

    Attributes:
        default_kernel(str): The default kernel name for next boot
    """
    def parse_content(self, content):
        if not content:
            raise SkipException('Empty output')
        if len(content) != 1:
            raise ParseException('Invalid output: {0}', content)
        self.default_kernel = content[0].strip()
