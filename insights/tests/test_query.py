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

""" Test the query tool. """
import inspect

from insights import dr
from insights.tests import InputData
from insights.tools.query import load_obj, get_source, get_pydoc


def test_load_obj():
    assert load_obj("insights.dr") is dr
    assert load_obj("insights.tests.InputData") is InputData
    assert load_obj("foo.bar") is None


def test_get_source():
    assert get_source("insights.dr") == inspect.getsource(dr)
    assert get_source("insights.tests.InputData") == inspect.getsource(InputData)
    assert get_source("foo.bar") is None


def test_get_pydoc():
    assert get_pydoc("insights.dr") is not None
    assert get_pydoc("insights.tests.InputData") is not None
    assert get_pydoc("foo.bar") is None
