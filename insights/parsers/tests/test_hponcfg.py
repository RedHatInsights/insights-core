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

from insights.parsers.hponcfg import HponConf
from insights.tests import context_wrap

HPONCFG = """
HP Lights-Out Online Configuration utility
Version 4.3.1 Date 05/02/2014 (c) Hewlett-Packard Company, 2014
Firmware Revision = 1.40 Device type = iLO 4 Driver name = hpilo
Host Information:
                        Server Name: foo.example.com
                        Server Number:
"""


def test_hponcfg():

    conf = HponConf(context_wrap(HPONCFG))

    assert "1.40" == conf.firmware_revision
    assert "iLO 4" == conf.device_type
    assert "hpilo" == conf.driver_name
    assert "foo.example.com" == conf['server_name']
    assert "" == conf['server_number']
