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

import tempfile
import insights.client.schedule as sched
from insights.client.config import InsightsConfig


def test_set_daily():
    target = tempfile.mktemp()
    config = InsightsConfig()
    with tempfile.NamedTemporaryFile() as source:
        schedule = sched.get_scheduler(config, source.name, target)
        assert not schedule.active
        assert schedule.set_daily()
        assert schedule.active
        schedule.remove_scheduling()
        assert not schedule.active


def test_failed_removal():
    """
    Just verifying that trying to remove scheduling does not raise an exception
    """
    target = tempfile.mktemp()
    config = InsightsConfig()
    with tempfile.NamedTemporaryFile() as source:
        schedule = sched.get_scheduler(config, source.name, target)
        schedule.remove_scheduling()
