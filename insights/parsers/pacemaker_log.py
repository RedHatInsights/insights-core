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
PacemakerLog - file ``/var/log/pacemaker.log``
==============================================
"""

from .. import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.pacemaker_log)
class PacemakerLog(LogFileOutput):
    """
    Read the pacemaker log file.  Uses the ``LogFileOutput`` class parser
    functionality.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput`


    Sample pacemaker.log::

        Aug 21 12:58:40 [11656] example.redhat.com        cib:     info: crm_client_destroy: 	Destroying 0 events
        Aug 21 12:59:53 [11655] example.redhat.com pacemakerd:     info: pcmk_quorum_notification: 	Membership 12: quorum retained (3)
        Aug 21 12:59:53 [11661] example.redhat.com       crmd:     info: pcmk_quorum_notification: 	Membership 12: quorum retained (3)
        Aug 21 12:59:53 [11655] example.redhat.com pacemakerd:     info: pcmk_quorum_notification: 	Membership 12: quorum retained (3)

    .. note::
        Because pacemaker timestamps by default have no year, the
        year of the logs will be inferred from the year in your timestamp.
        This will also work around December/January crossovers.

    Examples:
        >>> pm = shared(PacemakerLog)
        >>> pm.get('crmd')[0]['raw_message']
        'Aug 21 12:59:53 [11661] example.redhat.comm       crmd:     info: pcmk_quorum_notification: 	Membership 12: quorum retained (3)'
        >>> from datetime import datetime
        >>> len(list(pm.get_after(datetime(21, 8, 2017, 12, 59, 50))))
        3
    """
    time_format = '%b %d %H:%M:%S'
