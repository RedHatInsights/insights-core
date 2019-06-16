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

import pytest
from insights.core import marshalling


def mar_unmar(o, use_value_list=False):
    marshalled = marshalling.marshal(o, use_value_list)
    unmarshalled = marshalling.unmarshal(marshalled)
    return marshalled, unmarshalled


def test_string_marshal():
    flag = "TEST_FLAG"
    _, unmarshalled = mar_unmar(flag)
    assert unmarshalled == {flag: True}


def test_dict_marshal():
    doc = {"foo": "bar"}
    _, unmarshalled = mar_unmar(doc)
    assert unmarshalled == doc


def test_bad_returns():
    with pytest.raises(TypeError):
        marshalling.marshal(True)
    with pytest.raises(TypeError):
        marshalling.marshal(1)
    with pytest.raises(TypeError):
        marshalling.marshal(1.0)
    with pytest.raises(TypeError):
        marshalling.marshal([])
    with pytest.raises(TypeError):
        marshalling.marshal(())
    with pytest.raises(TypeError):
        marshalling.marshal(set())


def test_none_marshal():
    ma, um = mar_unmar(None)
    assert um is None


def test_value_list():
    ma, um = mar_unmar("test", use_value_list=True)
    assert um == {"test": [True]}
