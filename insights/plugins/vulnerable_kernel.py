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

from insights import make_fail, rule
from insights.parsers.uname import Uname


@rule(Uname)
def report(uname):
    if uname.fixed_by('2.6.32-431.11.2.el6', introduced_in='2.6.32-431.el6'):
        return make_fail("VULNERABLE_KERNEL", kernel=uname.kernel)
