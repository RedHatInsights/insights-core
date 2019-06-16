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
Kernel Samepage Merging state - file ``/sys/kernel/mm/ksm/run``
===============================================================

This module offers the ``is_running`` parser function, which returns a
dictionary with one key: 'running', whose value is the state of whether
Kernel Samepage Merging is turned on.

Examples:

    >>> ksm = shared[is_running]
    >>> ksm['running']
    False
"""

from .. import parser
from insights.specs import Specs


@parser(Specs.ksmstate)
def is_running(context):
    """
    Check if Kernel Samepage Merging is turned on. Returns 'True' if KSM is
    on (i.e. ``/sys/kernel/mm/ksm/run`` is '1') or 'False' if not.
    """
    ksminfo = {}
    ksminfo['running'] = (context.content[0].split()[0] == '1')
    return ksminfo
