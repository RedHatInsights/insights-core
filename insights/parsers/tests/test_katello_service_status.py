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

from ...tests import context_wrap
from ..katello_service_status import KatelloServiceStatus

KS_OUT = """
pulp_celerybeat (pid 443) is running.
celery init v10.0.
Using config script: /etc/default/pulp_workers
node reserved_resource_worker-0 (pid 902) is running...
node reserved_resource_worker-1 (pid 921) is running...
node reserved_resource_worker-2 (pid 938) is running...
node reserved_resource_worker-3 (pid 959) is running...
celery init v10.0.
Using config script: /etc/default/pulp_resource_manager
node resource_manager (pid 691) is running...
tomcat6 is stopped                                         [  OK  ]
dynflow_executor is running.
dynflow_executor_monitor is running.
httpd is stopped
Some services failed to status: tomcat6,httpd
"""

KS_OUT_1 = """
Some services failed to status: httpd
"""

KS_OUT_2 = """
Using config script: /etc/default/pulp_resource_manager
node resource_manager (pid 691) is running...
httpd (pid  16006) is running..
tomcat6 (pid 15560) is running...                          [  OK  ]
Success!
"""


def test_kss():
    kss = KatelloServiceStatus(context_wrap(KS_OUT))
    assert kss.failed_services == ['tomcat6', 'httpd']
    assert not kss.is_ok
    kss = KatelloServiceStatus(context_wrap(KS_OUT_1))
    assert kss.failed_services == ['httpd']
    assert not kss.is_ok
    kss = KatelloServiceStatus(context_wrap(KS_OUT_2))
    assert kss.failed_services == []
    assert kss.is_ok
