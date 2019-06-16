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
nova_log - files ``/var/log/nova/*.log``
========================================
This module contains classes to parse logs under ``/var/log/nova/``
"""
from .. import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.nova_api_log)
class NovaApiLog(LogFileOutput):
    """Class for parsing the ``/var/log/nova/nova-api.log`` file.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput`
    """
    pass


@parser(Specs.nova_compute_log)
class NovaComputeLog(LogFileOutput):
    """Class for parsing the ``/var/log/nova/nova-compute.log`` file.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput`
    """
    pass
