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

from insights.client.auto_config import set_auto_configuration, _try_satellite6_configuration
from mock.mock import Mock, patch


@patch("insights.client.auto_config.rhsmCertificate", Mock())
@patch("insights.client.auto_config.open", Mock())
@patch("insights.client.auto_config._importInitConfig")
@patch("insights.client.auto_config.set_auto_configuration")
def test_rhsm_legacy_url(set_auto_configuration, initConfig):
    '''
    Ensure the correct host URL is selected for auto_config on a legacy RHSM upload
    '''
    initConfig().get.side_effect = ['subscription.rhsm.redhat.com', '443', '', '', '', '', '']
    config = Mock(base_url=None, upload_url=None, legacy_upload=True, insecure_connection=False)
    _try_satellite6_configuration(config)
    set_auto_configuration.assert_called_with(config, 'cert-api.access.redhat.com', None, None, False)


@patch("insights.client.auto_config.rhsmCertificate", Mock())
@patch("insights.client.auto_config.open", Mock())
@patch("insights.client.auto_config._importInitConfig")
@patch("insights.client.auto_config.set_auto_configuration")
def test_rhsm_platform_url(set_auto_configuration, initConfig):
    '''
    Ensure the correct host URL is selected for auto_config on a platform RHSM upload
    '''
    initConfig().get.side_effect = ['subscription.rhsm.redhat.com', '443', '', '', '', '', '']
    config = Mock(base_url=None, upload_url=None, legacy_upload=False, insecure_connection=False)
    _try_satellite6_configuration(config)
    # set_auto_configuration.assert_called_with(config, 'cloud.redhat.com', None, None, False)
    set_auto_configuration.assert_called_with(config, 'cert-api.access.redhat.com', None, None, False)


@patch("insights.client.auto_config.rhsmCertificate", Mock())
@patch("insights.client.auto_config.open", Mock())
@patch("insights.client.auto_config._importInitConfig")
@patch("insights.client.auto_config.set_auto_configuration")
def test_sat_legacy_url(set_auto_configuration, initConfig):
    '''
    Ensure the correct host URL is selected for auto_config on a legacy Sat upload
    '''
    initConfig().get.side_effect = ['test.satellite.com', '443', '', '', '', '', 'test_cert']
    config = Mock(base_url=None, upload_url=None, legacy_upload=True, insecure_connection=False)
    _try_satellite6_configuration(config)
    set_auto_configuration.assert_called_with(config, 'test.satellite.com:443/redhat_access', 'test_cert', None, True)


@patch("insights.client.auto_config.rhsmCertificate", Mock())
@patch("insights.client.auto_config.open", Mock())
@patch("insights.client.auto_config._importInitConfig")
@patch("insights.client.auto_config.set_auto_configuration")
def test_sat_platform_url(set_auto_configuration, initConfig):
    '''
    Ensure the correct host URL is selected for auto_config on a platform Sat upload
    '''
    initConfig().get.side_effect = ['test.satellite.com', '443', '', '', '', '', 'test_cert']
    config = Mock(base_url=None, upload_url=None, legacy_upload=False, insecure_connection=False)
    _try_satellite6_configuration(config)
    set_auto_configuration.assert_called_with(config, 'test.satellite.com:443/redhat_access', 'test_cert', None, True)


@patch("insights.client.auto_config.verify_connectivity", Mock())
def test_rhsm_legacy_base_url_configured():
    '''
    Ensure the correct base URL is assembled for a legacy RHSM upload
    '''
    config = Mock(base_url=None, upload_url=None, legacy_upload=True, insecure_connection=False, proxy=None)
    set_auto_configuration(config, 'cert-api.access.redhat.com', None, None, False)
    assert config.base_url == 'cert-api.access.redhat.com/r/insights'


@patch("insights.client.auto_config.verify_connectivity", Mock())
def test_rhsm_platform_base_url_configured():
    '''
    Ensure the correct base URL is assembled for a platform RHSM upload
    '''
    config = Mock(base_url=None, upload_url=None, legacy_upload=False, insecure_connection=False, proxy=None)
    # set_auto_configuration(config, 'cloud.redhat.com', None, None, False)
    # assert config.base_url == 'cloud.redhat.com/api'
    # [CIRCUS MUSIC]
    set_auto_configuration(config, 'cert-api.access.redhat.com', None, None, False)
    assert config.base_url == 'cert-api.access.redhat.com/r/insights/platform'


@patch("insights.client.auto_config.verify_connectivity", Mock())
def test_sat_legacy_base_url_configured():
    '''
    Ensure the correct base URL is assembled for a legacy RHSM upload
    '''
    config = Mock(base_url=None, upload_url=None, legacy_upload=True, insecure_connection=False, proxy=None)
    set_auto_configuration(config, 'test.satellite.com:443/redhat_access', 'test_cert', None, True)
    assert config.base_url == 'test.satellite.com:443/redhat_access/r/insights'


@patch("insights.client.auto_config.verify_connectivity", Mock())
def test_sat_platform_base_url_configured():
    '''
    Ensure the correct base URL is assembled for a platform RHSM upload
    '''
    config = Mock(base_url=None, upload_url=None, legacy_upload=False, insecure_connection=False, proxy=None)
    set_auto_configuration(config, 'test.satellite.com:443/redhat_access', 'test_cert', None, True)
    assert config.base_url == 'test.satellite.com:443/redhat_access/r/insights/platform'
