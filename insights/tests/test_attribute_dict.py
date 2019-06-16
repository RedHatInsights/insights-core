# -*- coding: UTF-8 -*-
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

from insights.core import AttributeDict

DICT = {'dmode': '0500', 'relatime': True, 'uid': '0',
        'iocharset': 'utf8', 'gid': '0', 'mode': '0400', 'ro': True,
        'nosuid': True, 'uhelper': 'udisks2', 'nodev': True}


def test_attribute_dict():
    d_obj = AttributeDict(DICT)
    assert d_obj['dmode'] == '0500'
    assert d_obj.get('relatime') is True
    assert d_obj.nosuid is True
    assert 'uid' in d_obj
    assert d_obj.get('mode', None) == '0400'
    assert d_obj.get('xmode', None) is None
    for d, v in d_obj.items():
        if d.startswith('nod'):
            assert v is True
