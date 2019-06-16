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

from insights.tests import deep_compare


def test_deep_compare():
    """
    Tests that deep_compare() doesn't modify the objects it compares.
    """
    x_list = [8, 5, 3, 1, 2, 9, 5]
    x_list_backup = [8, 5, 3, 1, 2, 9, 5]
    b_tuple = (8, 5, 3, 1, 2, 9, 5)
    b_tuple_backup = (8, 5, 3, 1, 2, 9, 5)
    a = {"4d": 20, "5a": 10, "3b": 15, "7c": 5, "x": x_list,
         "b": b_tuple}
    b = {"4d": 20, "5a": 10, "3b": 15, "7c": 5, "x": [8, 5, 3, 1, 2, 9, 5],
         "b": (8, 5, 3, 1, 2, 9, 5)}
    c = {"4d": 20, "5a": 10, "3b": 15, "7c": 5, "x": [8, 5, 3, 1, 2, 9, 5],
         "b": (8, 5, 3, 1, 2, 9, 5)}
    d = {"4d": 20, "5a": 10, "3b": 15, "7c": 5, "x": [0, 8, 5, 3, 1, 2, 9, 5],
         "b": (8, 5, 3, 1, 2, 9, 5)}
    # sanity test before any manipulation
    # python can compare dicts natively to this extent
    assert c != d
    assert a == b
    assert a == c
    assert b == c
    assert x_list == x_list_backup
    assert b_tuple == b_tuple_backup
    noexception = False
    try:
        deep_compare(a, b)
        noexception = True
    except:
        pass
    # deep_compare test - the original objects should stay unchanged
    assert noexception
    assert a == b
    assert a == c
    assert b == c
    assert x_list == x_list_backup
    assert b_tuple == b_tuple_backup
