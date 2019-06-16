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
getsebool - command ``/usr/sbin/getsebool -a``
==============================================

This parser returns the output of the ``getsebool``
command.

Sample ``getsebool -a`` output::

    webadm_manage_user_files --> off
    webadm_read_user_files --> off
    wine_mmap_zero_ignore --> off
    xdm_bind_vnc_tcp_port --> off
    ssh_keysign --> off

Examples:

    >>> "webadm_manage_user_files" in getsebool
    True
    >>> "tmpreaper_use_nfs" in getsebool
    False
    >>> getsebool['ssh_keysign']
    'off'
"""

from .. import parser, LegacyItemAccess, CommandParser
from . import SkipException
from insights.specs import Specs


@parser(Specs.getsebool)
class Getsebool(LegacyItemAccess, CommandParser):
    """
    The output of "getsebool" command is like following:

        tmpreaper_use_nfs --> off
        tmpreaper_use_samba --> off

    So we can return the value like {"tmpreaper_use_nfs":"off", "tmpreaper_use_samba":"off"}

    Raises:
        SkipException: When SELinux is not enabled.
    """

    def parse_content(self, content):
        if content and 'selinux is disabled' in content[0].lower():
            raise SkipException('SELinux is disabled')

        self.data = {}
        for line in content:
            key, value = line.split("-->")
            self.data[key.strip()] = value.strip()
