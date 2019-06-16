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
RHV Log Collector Analyzer
==========================

RHV Log Collector Analyzer is a tool that analyze RHV sosreports
and live systems.

This module provides processing for the output of
rhv-log-collector-analyzer --json which will be running
in a live system to detect possible issues.
"""

from .. import JSONParser, parser, CommandParser
from insights.specs import Specs


@parser(Specs.rhv_log_collector_analyzer)
class RhvLogCollectorJson(CommandParser, JSONParser):
    """
    Class to parse the output of ``rhv-log-collector-analyzer --json``.
    """
    pass
