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

from insights.client.auto_config import _try_satellite5_configuration
from mock.mock import Mock, patch


@patch("insights.client.auto_config.set_auto_configuration")
@patch("insights.client.auto_config.open", return_value=["serverURL=https://some-hostname/",
                                                                 "sslCACert=some-certificate",
                                                                 "enableProxy=0"])
@patch("insights.client.auto_config._read_systemid_file")
@patch("insights.client.auto_config.os.path.isfile", return_value=True)
def test_set_auto_configuration(isfile_mock, read_systemid_file_mock, open_mock, set_auto_configuration_mock):
    """
    set_auto_configuration_mock is called with correct arguments.
    """
    config_mock = Mock()
    _try_satellite5_configuration(config_mock)
    set_auto_configuration_mock.assert_called_once_with(config_mock,
                                                        "some-hostname/redhat_access",
                                                        "some-certificate",
                                                        None)
