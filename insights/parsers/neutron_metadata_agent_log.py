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
NeutronMetadataAgentLog - file ``/var/log/neutron/metadata-agent.log``
======================================================================
"""

from .. import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.neutron_metadata_agent_log)
class NeutronMetadataAgentLog(LogFileOutput):
    """
      Parse the ``/var/log/neutron/metadata-agent.log`` file.

      .. note::
          Please refer to its super-class :class:`insights.core.LogFileOutput` for more
          details.

      Sample log lines::

          2018-06-08 17:29:55.894 11770 WARNING neutron.agent.metadata.agent [-] Server does not support metadata RPC, fallback to using neutron client
          2018-06-08 17:29:55.907 11770 ERROR neutron.agent.metadata.agent [-] Unexpected error
          2018-06-08 17:29:56.126 11770 TRACE neutron.agent.metadata.agent Traceback (most recent call last):
          2018-06-08 17:29:56.126 11770 TRACE neutron.agent.metadata.agent   File "/usr/lib/python2.7/site-packages/neutron/agent/metadata/agent.py", line 109, in __call__
          2018-06-08 17:29:56.126 11770 TRACE neutron.agent.metadata.agent     self._authenticate_keystone()
          2018-06-08 17:29:56.126 11770 TRACE neutron.agent.metadata.agent   File "/usr/lib/python2.7/site-packages/neutronclient/client.py", line 218, in _authenticate_keystone
          2018-06-08 17:29:56.126 11770 TRACE neutron.agent.metadata.agent     raise exceptions.Unauthorized(message=resp_body)
          2018-06-08 17:29:56.126 11770 TRACE neutron.agent.metadata.agent Unauthorized: {"error": {"message": "The resource could not be found.", "code": 404, "title": "Not Found"}}

      Examples:
          >>> len(metadata_agent_log.get("Server does not support metadata RPC, fallback to using neutron client")) == 1
          True
          >>> from datetime import datetime
          >>> len(list(metadata_agent_log.get_after(datetime(2018, 6, 8, 17, 29, 56))))
          6

      """
    pass
