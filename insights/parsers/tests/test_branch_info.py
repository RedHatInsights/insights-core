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

from insights.parsers.branch_info import BranchInfo
from insights.tests import context_wrap

bi_conf_content = """
{"remote_branch": -1, "remote_leaf": -1}
""".strip()


def test_settings_yml():
    ctx = context_wrap(bi_conf_content)
    ctx.content = bi_conf_content
    result = BranchInfo(ctx)
    assert result.data['remote_branch'] == -1
    assert result.data['remote_leaf'] == -1
