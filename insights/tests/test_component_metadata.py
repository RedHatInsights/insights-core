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

from insights.core import dr


class stage(dr.ComponentType):
    metadata = {"description": "A processing stage."}


@stage()
def report():
    return "this is a regular report"


@stage(metadata={"description": "Reports stuff about things."})
def special_report():
    return "this is a special report"


def test_component_metadata():
    msg = "A processing stage."
    special_msg = "Reports stuff about things."
    assert dr.get_metadata(report).get("description") == msg
    assert dr.get_metadata(special_report).get("description") == special_msg
