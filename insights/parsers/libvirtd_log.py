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
LibVirtdLog - file ``/var/log/libvirt/libvirtd.log``
====================================================

This is a fairly simple parser to read the logs of libvirtd.  It uses the
LogFileOutput parser class.

Sample input::

    2013-10-23 17:32:19.909+0000: 14069: debug : do_open:1174 : trying driver 1 (ESX) ...
    2013-10-23 17:32:19.909+0000: 14069: debug : do_open:1180 : driver 1 ESX returned DECLINED
    2013-10-23 17:32:19.909+0000: 14069: debug : do_open:1174 : trying driver 2 (remote) ...
    2013-10-23 17:32:19.957+0000: 14069: error : virNetTLSContextCheckCertDN:418 : Certificate [session] owner does not match the hostname AA.BB.CC.DD <============= IP Address
    2013-10-23 17:32:19.957+0000: 14069: warning : virNetTLSContextCheckCertificate:1102 : Certificate check failed Certificate [session] owner does not match the hostname AA.BB.CC.DD
    2013-10-23 17:32:19.957+0000: 14069: error : virNetTLSContextCheckCertificate:1105 : authentication failed: Failed to verify peer's certificate

Examples:

    >>> LibVirtdLog.filters.append('NetTLSContext')
    >>> LibVirtdLog.token_scan('check_failed', 'Certificate check failed')
    >>> virtlog = shared[LibVirtdLog]
    >>> len(virtlog.lines) # All lines, before filtering
    6
    >>> len(virtlog.get('NetTLSContext')) # After filtering
    3
    >>> virtlog.check_failed
    True

"""

from .. import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.libvirtd_log)
class LibVirtdLog(LogFileOutput):
    """
    Parse the ``/var/log/libvirt/libvirtd.log`` log file.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput`
    """
    pass
