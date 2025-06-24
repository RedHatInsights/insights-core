from insights.client.auto_config import set_auto_configuration, _try_satellite6_configuration, try_auto_configuration
from mock.mock import Mock, patch


@patch("insights.client.auto_config.rhsmCertificate", Mock())
@patch("insights.client.auto_config.open", Mock())
@patch("insights.client.auto_config._importInitConfig")
@patch("insights.client.auto_config.set_auto_configuration")
def test_rhsm_legacy_url(set_auto_configuration, initConfig):
    '''
    Ensure the correct host URL is selected for auto_config on a legacy RHSM upload
    '''
    initConfig().get.side_effect = ['subscription.rhsm.redhat.com', '443', '', '', '', '', '', '']
    config = Mock(base_url=None, upload_url=None, legacy_upload=True)
    _try_satellite6_configuration(config)
    set_auto_configuration.assert_called_with(config, 'cert-api.access.redhat.com', None, None, False, False, rhsm_no_proxy=None)


@patch("insights.client.auto_config.rhsmCertificate", Mock())
@patch("insights.client.auto_config.open", Mock())
@patch("insights.client.auto_config._importInitConfig")
@patch("insights.client.auto_config.set_auto_configuration")
def test_rhsm_platform_url(set_auto_configuration, initConfig):
    '''
    Ensure the correct host URL is selected for auto_config on a platform RHSM upload
    '''
    initConfig().get.side_effect = ['subscription.rhsm.redhat.com', '443', '', '', '', '', '', '']
    config = Mock(base_url=None, upload_url=None, legacy_upload=False)
    _try_satellite6_configuration(config)
    # set_auto_configuration.assert_called_with(config, 'console.redhat.com', None, None, False)
    set_auto_configuration.assert_called_with(config, 'cert-api.access.redhat.com', None, None, False, False, rhsm_no_proxy=None)


@patch("insights.client.auto_config.rhsmCertificate", Mock())
@patch("insights.client.auto_config.open", Mock())
@patch("insights.client.auto_config._importInitConfig")
@patch("insights.client.auto_config.set_auto_configuration")
def test_rhsm_stage_legacy_url(set_auto_configuration, initConfig):
    '''
    Ensure the correct host URL is selected for auto_config on a legacy staging RHSM upload

    This will still force legacy_upload=False as there is no classic staging env,
    so the result is the same as platform upload.

    '''
    initConfig().get.side_effect = ['subscription.rhsm.stage.redhat.com', '443', '', '', '', '', '', '']
    config = Mock(base_url=None, upload_url=None, legacy_upload=True)
    _try_satellite6_configuration(config)
    # config.legacy_upload is modified in the function
    config.legacy_upload = False
    set_auto_configuration.assert_called_with(config, 'cert.cloud.stage.redhat.com', None, None, False, True, rhsm_no_proxy=None)


@patch("insights.client.auto_config.rhsmCertificate", Mock())
@patch("insights.client.auto_config.open", Mock())
@patch("insights.client.auto_config._importInitConfig")
@patch("insights.client.auto_config.set_auto_configuration")
def test_rhsm_stage_platform_url(set_auto_configuration, initConfig):
    '''
    Ensure the correct host URL is selected for auto_config on a platform staging RHSM upload
    '''
    initConfig().get.side_effect = ['subscription.rhsm.stage.redhat.com', '443', '', '', '', '', '', '']
    config = Mock(base_url=None, upload_url=None, legacy_upload=False)
    _try_satellite6_configuration(config)
    set_auto_configuration.assert_called_with(config, 'cert.cloud.stage.redhat.com', None, None, False, True, rhsm_no_proxy=None)


@patch("insights.client.auto_config.rhsmCertificate", Mock())
@patch("insights.client.auto_config.open", Mock())
@patch("insights.client.auto_config._importInitConfig")
@patch("insights.client.auto_config.set_auto_configuration")
def test_sat_legacy_url(set_auto_configuration, initConfig):
    '''
    Ensure the correct host URL is selected for auto_config on a legacy Sat upload
    '''
    initConfig().get.side_effect = ['test.satellite.com', '443', '', '', '', '', '', 'test_cert']
    config = Mock(base_url=None, upload_url=None, legacy_upload=True)
    _try_satellite6_configuration(config)
    set_auto_configuration.assert_called_with(config, 'test.satellite.com:443/redhat_access', 'test_cert', None, True, False, rhsm_no_proxy=None)


@patch("insights.client.auto_config.rhsmCertificate", Mock())
@patch("insights.client.auto_config.open", Mock())
@patch("insights.client.auto_config._importInitConfig")
@patch("insights.client.auto_config.set_auto_configuration")
def test_sat_platform_url(set_auto_configuration, initConfig):
    '''
    Ensure the correct host URL is selected for auto_config on a platform Sat upload
    '''
    initConfig().get.side_effect = ['test.satellite.com', '443', '', '', '', '', '', 'test_cert']
    config = Mock(base_url=None, upload_url=None, legacy_upload=False)
    _try_satellite6_configuration(config)
    set_auto_configuration.assert_called_with(config, 'test.satellite.com:443/redhat_access', 'test_cert', None, True, False, rhsm_no_proxy=None)


@patch("insights.client.auto_config.verify_connectivity", Mock())
def test_rhsm_legacy_base_url_configured():
    '''
    Ensure the correct base URL is assembled for a legacy RHSM upload
    '''
    config = Mock(base_url=None, upload_url=None, legacy_upload=True, proxy=None)
    set_auto_configuration(config, 'cert-api.access.redhat.com', None, None, False, False)
    assert config.base_url == 'cert-api.access.redhat.com/r/insights'


@patch("insights.client.auto_config.verify_connectivity", Mock())
def test_rhsm_platform_base_url_configured():
    '''
    Ensure the correct base URL is assembled for a platform RHSM upload
    '''
    config = Mock(base_url=None, upload_url=None, legacy_upload=False, proxy=None)
    # set_auto_configuration(config, 'console.redhat.com', None, None, False)
    # assert config.base_url == 'console.redhat.com/api'
    # [CIRCUS MUSIC]
    set_auto_configuration(config, 'cert-api.access.redhat.com', None, None, False, False)
    # assert config.base_url == 'cert-api.access.redhat.com/r/insights/platform'
    assert config.base_url == 'cert-api.access.redhat.com/r/insights'


@patch("insights.client.auto_config.verify_connectivity", Mock())
def test_sat_legacy_base_url_configured():
    '''
    Ensure the correct base URL is assembled for a legacy RHSM upload
    '''
    config = Mock(base_url=None, upload_url=None, legacy_upload=True, proxy=None)
    set_auto_configuration(config, 'test.satellite.com:443/redhat_access', 'test_cert', None, True, False)
    assert config.base_url == 'test.satellite.com:443/redhat_access/r/insights'


@patch("insights.client.auto_config.verify_connectivity", Mock())
def test_sat_platform_base_url_configured():
    '''
    Ensure the correct base URL is assembled for a platform RHSM upload
    '''
    config = Mock(base_url=None, upload_url=None, legacy_upload=False, proxy=None)
    set_auto_configuration(config, 'test.satellite.com:443/redhat_access', 'test_cert', None, True, False)
    # assert config.base_url == 'test.satellite.com:443/redhat_access/r/insights/platform'
    assert config.base_url == 'test.satellite.com:443/redhat_access/r/insights'


@patch("insights.client.auto_config.verify_connectivity", Mock())
def test_platform_path_added():
    '''
    Ensure /platform is added when legacy_upload is false
    Ensure it's not added when legacy_upload is true
    '''
    # auto_config=True, legacy_upload=True
    config = Mock(base_url='test.satellite.com:443/redhat_access/r/insights', auto_config=True, legacy_upload=True, offline=False)
    try_auto_configuration(config)
    assert config.base_url == 'test.satellite.com:443/redhat_access/r/insights'

    # auto_config=True, legacy_upload=False
    config = Mock(base_url='test.satellite.com:443/redhat_access/r/insights', auto_config=True, legacy_upload=False, offline=False)
    try_auto_configuration(config)
    assert config.base_url == 'test.satellite.com:443/redhat_access/r/insights/platform'

    # auto_config=False, legacy_upload=True
    config = Mock(base_url='test.satellite.com:443/redhat_access/r/insights', auto_config=False, legacy_upload=True, offline=False)
    try_auto_configuration(config)
    assert config.base_url == 'test.satellite.com:443/redhat_access/r/insights'

    # auto_config=False, legacy_upload=False
    config = Mock(base_url='test.satellite.com:443/redhat_access/r/insights', auto_config=False, legacy_upload=False, offline=False)
    try_auto_configuration(config)
    assert config.base_url == 'test.satellite.com:443/redhat_access/r/insights/platform'


@patch("insights.client.auto_config._try_satellite6_configuration", Mock())
def test_platform_path_added_cloud_redhat():
    '''
    Ensure /platform is added when legacy_upload is false
    for any base_url ending in /r/insights, otherwise not added
    '''
    # classic API
    config = Mock(base_url='cert-api.access.redhat.com/r/insights', auto_config=True, legacy_upload=False, offline=False)
    try_auto_configuration(config)
    assert config.base_url == 'cert-api.access.redhat.com/r/insights/platform'

    # satellite
    config = Mock(base_url='test.satellite.com:443/redhat_access/r/insights', auto_config=True, legacy_upload=False, offline=False)
    try_auto_configuration(config)
    assert config.base_url == 'test.satellite.com:443/redhat_access/r/insights/platform'

    # console.redhat.com compatibility layer - classic API hosted on c.rh.c
    config = Mock(base_url='console.redhat.com/r/insights', auto_config=True, legacy_upload=False, offline=False)
    try_auto_configuration(config)
    assert config.base_url == 'console.redhat.com/r/insights/platform'

    # console.redhat.com API directly connected
    config = Mock(base_url='console.redhat.com/api', auto_config=True, legacy_upload=False, offline=False)
    try_auto_configuration(config)
    assert config.base_url == 'console.redhat.com/api'


@patch("insights.client.auto_config.verify_connectivity", Mock())
def test_rhsm_stage_legacy_base_url_configured():
    '''
    Ensure the correct base URL is assembled for a legacy staging RHSM upload

    This will still force legacy_upload=False as there is no classic staging env,
    so the result is the same as platform upload.
    '''
    config = Mock(base_url=None, upload_url=None, legacy_upload=True, proxy=None)
    set_auto_configuration(config, 'cert.cloud.stage.redhat.com', None, None, False, True)
    assert config.base_url == 'cert.cloud.stage.redhat.com/api'


@patch("insights.client.auto_config.verify_connectivity", Mock())
def test_rhsm_stage_platform_base_url_configured():
    '''
    Ensure the correct base URL is assembled for a platform staging RHSM upload
    '''
    config = Mock(base_url=None, upload_url=None, legacy_upload=False, proxy=None)
    set_auto_configuration(config, 'cert.cloud.stage.redhat.com', None, None, False, True)
    assert config.base_url == 'cert.cloud.stage.redhat.com/api'
