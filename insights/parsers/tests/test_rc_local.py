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

from insights.parsers.rc_local import RcLocal
from insights.tests import context_wrap

RC_LOCAL_DATA = """
#!/bin/sh
#
# This script will be executed *after* all the other init scripts.
# You can put your own initialization stuff in here if you don't
# want to do the full Sys V style init stuff.

touch /var/lock/subsys/local
echo never > /sys/kernel/mm/redhat_transparent_hugepage/enabled
""".strip()


def test_rc_local():
    rc_local = RcLocal(context_wrap(RC_LOCAL_DATA))
    assert len(rc_local.data) == 2
    assert rc_local.data[0] == 'touch /var/lock/subsys/local'
    assert rc_local.get('kernel') == ['echo never > /sys/kernel/mm/redhat_transparent_hugepage/enabled']
