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
rhn_schema_version - Command ``/usr/bin/rhn-schema-version``
============================================================
Parse the output of command ``/usr/bin/rhn-schema-version``.

"""
from .. import parser
from insights.specs import Specs


@parser(Specs.rhn_schema_version)
def rhn_schema_version(context):
    """
    Function to parse the output of command ``/usr/bin/rhn-schema-version``.

    Sample input::

        5.6.0.10-2.el6sat

    Examples:
        >>> db_ver = shared[rhn_schema_version]
        >>> db_ver
        '5.6.0.10-2.el6sat'

    """
    if context.content:
        content = context.content
        if len(content) == 1 and 'No such' not in content[0]:
            ver = content[0].strip()
            if ver:
                return ver
