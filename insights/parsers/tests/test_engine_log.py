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

from insights.parsers.engine_log import EngineLog
from insights.tests import context_wrap

from datetime import datetime

ENGINE_LOG = """
2016-05-18 13:21:21,115 INFO [org.ovirt.engine.core.bll.scheduling.policyunits.EvenGuestDistributionBalancePolicyUnit] (DefaultQuartzScheduler_Worker-95) [5bc194fa] There is no host with more than 8 running guests, no balancing is needed
2016-05-18 14:00:51,272 INFO [org.ovirt.engine.core.vdsbroker.VdsUpdateRunTimeInfo] (DefaultQuartzScheduler_Worker-95) [5bc194fa] VM ADLG8201 ab289661-bbaa-4d27-a67a-ad20626f60f0 moved from PoweringUp --> Paused
2016-05-18 14:00:51,318 ERROR [org.ovirt.engine.core.dal.dbbroker.auditloghandling.AuditLogDirector] (DefaultQuartzScheduler_Worker-95) [5bc194fa] Correlation ID: null, Call Stack: null, Custom Event ID: -1, Message: VM ADLG8201 has paused due to storage I/O problem.
2016-05-18 14:00:51,317 ERROR [org.ovirt.engine.core.dal.dbbroker.auditloghandling.AuditLogDirector] (DefaultQuartzScheduler_Worker-95) [5bc194fa] Correlation ID: null, Call Stack: null, Custom Event ID: -1, Message: VM ADLG8201 has paused due to storage I/O problem.
"""

matched_lines = ['2016-05-18 14:00:51,318 ERROR [org.ovirt.engine.core.dal.dbbroker.auditloghandling.AuditLogDirector] (DefaultQuartzScheduler_Worker-95) [5bc194fa] Correlation ID: null, Call Stack: null, Custom Event ID: -1, Message: VM ADLG8201 has paused due to storage I/O problem.',
                '2016-05-18 14:00:51,317 ERROR [org.ovirt.engine.core.dal.dbbroker.auditloghandling.AuditLogDirector] (DefaultQuartzScheduler_Worker-95) [5bc194fa] Correlation ID: null, Call Stack: null, Custom Event ID: -1, Message: VM ADLG8201 has paused due to storage I/O problem.']


def test_engine_log():
    engine_log_obj = EngineLog(context_wrap(ENGINE_LOG))
    assert "storage I/O problem." in engine_log_obj
    assert matched_lines == [i['raw_message'] for i in engine_log_obj.get('has paused due to storage I/O problem')]
    assert len(list(engine_log_obj.get_after(datetime(2016, 5, 18, 14, 0, 0)))) == 3
