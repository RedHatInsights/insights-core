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

from insights import combiner
from insights.tests import archive_provider, InputData


@combiner()
def one():
    return 1


@combiner()
def two():
    return 2


@combiner(one, two)
def three(x, y):
    return x + y


@archive_provider(three)
def integration_tests():
    data = InputData()
    data.add_component(two, 5)
    yield data, 6
