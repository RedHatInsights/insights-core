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

from insights.tests import context_wrap
from insights.parsers.rhn_schema_version import rhn_schema_version

schema_content_ok = """
5.6.0.10-2.el6sat
""".strip()

schema_content_no = """
-bash: /usr/bin/rhn-schema-version: No such file or directory
""".strip()


def test_rhn_schema_version():
    result = rhn_schema_version(context_wrap(schema_content_ok))
    assert result == "5.6.0.10-2.el6sat"
    result = rhn_schema_version(context_wrap(schema_content_no))
    assert result is None
