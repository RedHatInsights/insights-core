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
Kernel system control information
=================================

Shared parsers for parsing file ``/etc/sysctl.conf`` and command ``sysctl -a``.

Parsers included in this module are:

Sysctl - command ``sysctl -a``
------------------------------

SysctlConf - file ``/etc/sysctl.conf``
--------------------------------------

SysctlConfInitramfs - command ``lsinitrd``
------------------------------------------

"""
from .. import Parser, LogFileOutput, parser, LegacyItemAccess, CommandParser
from ..parsers import split_kv_pairs
from insights.specs import Specs


@parser(Specs.sysctl_conf)
class SysctlConf(Parser):
    """Parse `/etc/sysctl.conf` file

    Sample input::

        # sysctl.conf sample
        #
          kernel.domainname = example.com

        ; this one has a space which will be written to the sysctl!
          kernel.modprobe = /sbin/mod probe

    Attributes
    ----------
    data: OrderedDict
        Dictionary containing key/value pairs for the lines in the
        configuration file.  Dictionary is in order keywords first
        appear in the lines.

    Examples
    --------
    >>> shared[SysctlConf].data['kernel.domainname']
    'example.com'
    >>> shared[SysctlConf].data['kernel.modprobe']
    '/sbin/mod probe'
    """

    def parse_content(self, content):
        # Valid comments are both # and ; so remove one locally,
        # other comments and blank lines are removed by split fxn.
        lines = [l for l in content if not l.strip().startswith(';')]
        self.data = split_kv_pairs(lines, ordered=True)


@parser(Specs.sysctl)
class Sysctl(LegacyItemAccess, CommandParser):
    """Parse the output of `sysctl -a` command.

    Sample input::

        kernel.domainname = example.com
        kernel.modprobe = /sbin/modprobe

    Examples
    --------
    >>> shared[Sysctl]['kernel.domainname']
    'example.com'
    >>> shared[Sysctl].get('kernel.modprobe')
    '/sbin/modprobe'
    >>> 'kernel.modules_disabled' in shared[Sysctl]
    False
    """

    def parse_content(self, content):
        self.data = split_kv_pairs(content)


@parser(Specs.sysctl_conf_initramfs)
class SysctlConfInitramfs(CommandParser, LogFileOutput):
    """Shared parser for the output of ``lsinitrd`` applied to kdump
    initramfs images to view ``sysctl.conf`` and ``sysctl.d``
    configurations.

    For now, the file is treated as raw lines (as a ``LogFileOutput``
    parser.  This is because the output of the command, applied to
    multiple files to examine multiple files does not seem to be
    unambiguously parsible.

    Since the only plugins requiring the file to date "grep out"
    certain strings, this approach will suffice.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput`
    """
    pass
