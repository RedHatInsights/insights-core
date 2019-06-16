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

from insights.core.plugins import rule, make_fail, make_pass
from insights.parsers import installed_rpms, uname as uname_mod


@rule(optional=[installed_rpms.InstalledRpms, uname_mod.Uname])
def report(rpms, uname):
    if rpms is not None:
        bash_ver = rpms.get_max('bash')
        if uname is not None:
            return make_pass('PASS', bash_ver=bash_ver.nvr, uname_ver=uname.version)
        else:
            return make_fail('FAIL', bash_ver=bash_ver.nvr, path=rpms.file_path)

    # implicit return None
