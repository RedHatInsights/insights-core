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
SwiftLog - file ``/var/log/containers/swift/swift.log`` and ``/var/log/swift/swift.log``
========================================================================================
"""

from insights import parser, Syslog
from insights.specs import Specs


@parser(Specs.swift_log)
class SwiftLog(Syslog):
    """Class for parsing ``/var/log/containers/swift/swift.log`` and
    ``/var/log/swift/swift.log`` file.

    Provide access to swift log using the
    :class:`insights.core.Syslog` parser class.

    Sample ``swift.log`` file content::

      Sep 29 23:50:29 rh-server object-server: Starting object replication pass.
      Sep 29 23:50:29 rh-server object-server: Nothing replicated for 0.01691198349 seconds.
      Sep 29 23:50:29 rh-server object-server: Object replication complete. (0.00 minutes)
      Sep 29 23:50:38 rh-server container-server: Beginning replication run
      Sep 29 23:50:38 rh-server container-server: Replication run OVER
      Sep 29 23:50:38 rh-server container-server: Attempted to replicate 0 dbs in 0.00064 seconds (0.00000/s)

    Examples:

      >>> obj_server_lines = swift_log.get("object-server")
      >>> len(obj_server_lines)
      3
      >>> obj_server_lines[0].get("procname")
      'object-server'
      >>> obj_server_lines[0].get("message")
      'Starting object replication pass.'

    """
    pass
