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
getenforce - command ``/usr/sbin/getenforce``
=============================================

This very simple parser returns the output of the ``getenforce`` command.

Examples:

    >>> enforce = shared[getenforcevalue]
    >>> enforce['status']
    'Enforcing'
"""

from .. import parser
from insights.specs import Specs


@parser(Specs.getenforce)
def getenforcevalue(context):
    """
    The output of "getenforce" command is in one of "Enforcing", "Permissive",
    or "Disabled", so we can return the content directly.
    """
    return {"status": context.content[0]}
