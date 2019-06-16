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

import doctest
from insights.parsers import ls_origin_local_volumes_pods
from insights.parsers.ls_origin_local_volumes_pods import LsOriginLocalVolumePods
from insights.tests import context_wrap

LS_ORIGIN_LOCAL_VOLUME_PODS = """
total 0
drwxr-x---. 5 root root 71 Oct 18 23:20 5946c1f644096161a1242b3de0ee5875
drwxr-x---. 5 root root 71 Oct 18 23:24 6ea3d5cd-d34e-11e8-a142-001a4a160152
drwxr-x---. 5 root root 71 Oct 18 23:31 77d6d959-d34f-11e8-a142-001a4a160152
drwxr-x---. 5 root root 71 Oct 18 23:24 7ad952a0-d34e-11e8-a142-001a4a160152
drwxr-x---. 5 root root 71 Oct 18 23:24 7b63e8aa-d34e-11e8-a142-001a4a160152
""".strip()


def test_ls_origin_local_volumes_pods():
    ls_origin_local_volumes_pods = LsOriginLocalVolumePods(
        context_wrap(LS_ORIGIN_LOCAL_VOLUME_PODS,
                     path='insights_commands/ls_-l_.var.lib.origin.openshift.local.volumes.pods'))
    assert len(ls_origin_local_volumes_pods.pods) == 5
    assert ls_origin_local_volumes_pods.pods == [
        '5946c1f644096161a1242b3de0ee5875', '6ea3d5cd-d34e-11e8-a142-001a4a160152',
        '77d6d959-d34f-11e8-a142-001a4a160152', '7ad952a0-d34e-11e8-a142-001a4a160152',
        '7b63e8aa-d34e-11e8-a142-001a4a160152']


def test_ls_origin_local_volumes_pods_doc_examples():
    env = {
        'ls_origin_local_volumes_pods': LsOriginLocalVolumePods(
            context_wrap(LS_ORIGIN_LOCAL_VOLUME_PODS,
                         path='insights_commands/ls_-l_.var.lib.origin.openshift.local.volumes.pods')),
    }
    failed, total = doctest.testmod(ls_origin_local_volumes_pods, globs=env)
    assert failed == 0
