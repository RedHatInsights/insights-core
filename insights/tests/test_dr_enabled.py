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

from insights import combiner, dr

from insights.parsers.uname import Uname


def teardown_function(*args):
    for k in dr.ENABLED:
        dr.ENABLED[k] = True


@combiner()
def one():
    return 1


def test_enabled_string():
    assert dr.is_enabled("insights.core.context.HostContext")


def test_enabled_object():
    assert dr.is_enabled(Uname)


def test_disabled_string():
    dr.set_enabled("insights.core.context.HostContext", False)
    from insights.core.context import HostContext
    assert not dr.is_enabled(HostContext)


def test_disabled_object():
    dr.set_enabled(Uname, False)
    assert not dr.is_enabled(Uname)


def test_disabled_run():
    assert dr.ENABLED[one]
    broker = dr.run(dr.COMPONENTS[dr.GROUPS.single])
    assert one in broker

    dr.set_enabled(one, False)
    assert not dr.ENABLED[one]
    broker = dr.run(dr.COMPONENTS[dr.GROUPS.single])
    assert one not in broker
