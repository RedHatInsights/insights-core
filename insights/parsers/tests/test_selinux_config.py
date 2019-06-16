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

from insights.parsers.selinux_config import SelinuxConfig
from insights.tests import context_wrap

SELINUX_CONFIG = """
# This file controls the state of SELinux on the system.
# SELINUX= can take one of these three values:
#     enforcing - SELinux security policy is enforced.
#     permissive - SELinux prints warnings instead of enforcing.
#     disabled - No SELinux policy is loaded.
SELINUX=enforcing

 # SELINUXTYPE= can take one of three two values:
 #     targeted - Targeted processes are protected,
 #     minimum - Modification of targeted policy. Only selected processes are protected.
 #     mls - Multi Level Security protection.
SELINUXTYPE=targeted

"""


def test_selinux_config():
    selinux_config = SelinuxConfig(context_wrap(SELINUX_CONFIG)).data
    assert selinux_config["SELINUX"] == 'enforcing'
    assert selinux_config.get("SELINUXTYPE") == 'targeted'
    assert len(selinux_config) == 2
