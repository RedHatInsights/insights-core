# -*- coding: UTF-8 -*-
from insights.client.phase.v1 import post_update
from mock.mock import patch, MagicMock
from pytest import raises


def patch_insights_config(old_function):
    patcher = patch("insights.client.phase.v1.InsightsConfig",
                    **{"return_value.load_all.return_value.status": False,
                       "return_value.load_all.return_value.unregister": False,
                       "return_value.load_all.return_value.offline": False,
                       "return_value.load_all.return_value.enable_schedule": False,
                       "return_value.load_all.return_value.disable_schedule": False,
                       "return_value.load_all.return_value.analyze_container": False,
                       "return_value.load_all.return_value.display_name": False,
                       "return_value.load_all.return_value.register": False,
                       "return_value.load_all.return_value.diagnosis": None,
                       "return_value.load_all.return_value.list_specs": False,
                       "return_value.load_all.return_value.show_results": False,
                       "return_value.load_all.return_value.check_results": False,
                       "return_value.load_all.return_value.no_upload": False,
                       "return_value.load_all.return_value.module": False})
    return patcher(old_function)


@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_post_update_legacy_upload_off(insights_config, insights_client):
    """
    Registration is not called when platform upload
    """
    insights_config.return_value.load_all.return_value.legacy_upload = False
    try:
        post_update()
    except SystemExit:
        pass
    insights_client.return_value.register.assert_not_called()
    insights_client.return_value.get_machine_id.assert_called_once()


@patch("insights.client.phase.v1._get_rhsm_identity", return_value=True)
@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_post_update_legacy_upload_on(insights_config, insights_client, _get_rhsm_identity):
    """
    Registration is processed in legacy_upload=True
    """
    insights_config.return_value.load_all.return_value.legacy_upload = True
    insights_client.return_value.register.return_value = False
    try:
        post_update()
    except SystemExit:
        pass
    insights_client.return_value.register.assert_called_once()


@patch("insights.client.phase.v1._get_rhsm_identity", return_value=True)
@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_exit_ok(insights_config, insights_client, _get_rhsm_identity):
    """
    Support collection replaces the normal client run.
    """
    with raises(SystemExit) as exc_info:
        post_update()
    assert exc_info.value.code == 0


@patch("insights.client.phase.v1._get_rhsm_identity", return_value=True)
@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_post_update_no_upload(insights_config, insights_client, _get_rhsm_identity):
    """
    No-upload short circuits this phase
    """
    insights_config.return_value.load_all.return_value.no_upload = True
    try:
        post_update()
    except SystemExit:
        pass
    insights_client.return_value.register.assert_not_called()
    insights_client.return_value.get_machine_id.assert_called_once()


@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_post_update_register_machineid(insights_config, insights_client):
    """
    Client run with --register.
        If machine-id found, exit with 0 exit code (don't kill parent)
        Also enable scheduling.
    """
    insights_config.return_value.load_all.return_value.register = True
    insights_client.return_value.get_registration_status = MagicMock(return_value=False)
    insights_client.return_value.register = MagicMock(return_value=False)
    with raises(SystemExit) as exc_info:
        post_update()
    assert exc_info.value.code == 101
