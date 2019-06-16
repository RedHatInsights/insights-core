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
CephOsdTree
===========

Combiner provides the information about ceph osd tree. It
uses the results of the ``CephOsdTree``, ``CephInsights`` and ``CephOsdTreeText`` parsers.
The order from most preferred to least preferred is ``CephOsdTree``, ``CephInsights``, ``CephOsdTreeText``.

Examples:
    >>> type(cot)
    <class 'insights.combiners.ceph_osd_tree.CephOsdTree'>
    >>> cot['nodes'][0]['children']
    [-7, -3, -5, -9]
"""

from insights.core.plugins import combiner
from insights import LegacyItemAccess
from insights.parsers.ceph_cmd_json_parsing import CephOsdTree as CephOsdTreeParser
from insights.parsers.ceph_insights import CephInsights
from insights.parsers.ceph_osd_tree_text import CephOsdTreeText


@combiner([CephOsdTreeParser, CephInsights, CephOsdTreeText])
class CephOsdTree(LegacyItemAccess):
    """
    Combiner provides the information about ceph osd tree. It
    uses the results of the ``CephOsdTree``, ``CephInsights`` and ``CephOsdTreeText`` parsers.
    The order from most preferred to least preferred is ``CephOsdTree``, ``CephInsights``, ``CephOsdTreeText``.
    """

    def __init__(self, cot, ci, cott):
        if cot:
            self.data = cot
        elif ci:
            self.data = ci.data['osd_tree']
        else:
            self.data = cott
