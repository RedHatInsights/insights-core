# -*- coding: UTF-8 -*-

from contextlib import contextmanager
import os
from shutil import rmtree
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
                       "return_value.load_all.return_value.legacy_upload": False,
                       "return_value.load_all.return_value.diagnosis": None,
                       "return_value.load_all.return_value.payload": None,
                       "return_value.load_all.return_value.list_specs": False,
                       "return_value.load_all.return_value.show_results": False,
                       "return_value.load_all.return_value.check_results": False,
                       "return_value.load_all.return_value.no_upload": False,
                       "return_value.load_all.return_value.module": False})
    return patcher(old_function)

# DRY this at some point... for the love of god


@patch("insights.client.phase.v1.isfile", side_effect=[True])
@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_post_update_no_options_registered(insights_config, insights_client, _isfile):
    """
    Client run with no options.
        If registered, exit with 0 exit code (don't kill parent)
    """
    with raises(SystemExit) as exc_info:
        post_update()
    assert exc_info.value.code == 0
    insights_client.return_value.get_machine_id.assert_called_once()
    insights_client.return_value.clear_local_registration.assert_not_called()
    insights_client.return_value.set_display_name.assert_not_called()


@patch("insights.client.phase.v1.isfile", side_effect=[False])
@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_post_update_no_options_unregistered(insights_config, insights_client, _isfile):
    """
    Client run with no options.
        If unregistered, exit with 101 exit code (kill parent)
    """
    with raises(SystemExit) as exc_info:
        post_update()
    assert exc_info.value.code == 101
    insights_client.return_value.clear_local_registration.assert_not_called()
    insights_client.return_value.set_display_name.assert_not_called()


@patch("insights.client.phase.v1.isfile", side_effect=[False])
@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_post_update_no_options_err_reg_check(insights_config, insights_client, _isfile):
    """
    Client run with no options.
        If registration check fails, exit with 101 exit code
    """
    with raises(SystemExit) as exc_info:
        post_update()
    assert exc_info.value.code == 101
    insights_client.return_value.clear_local_registration.assert_not_called()
    insights_client.return_value.set_display_name.assert_not_called()


@patch("insights.client.phase.v1.isfile", side_effect=[True])
@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_post_update_check_status_registered(insights_config, insights_client, _isfile):
    """
    Just check status.
        If registered, exit with 100 exit code (kill parent)
    """
    insights_config.return_value.load_all.return_value.status = True
    with raises(SystemExit) as exc_info:
        post_update()
    assert exc_info.value.code == 100
    insights_client.return_value.clear_local_registration.assert_not_called()
    insights_client.return_value.set_display_name.assert_not_called()


@patch("insights.client.phase.v1.isfile", side_effect=[False])
@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_post_update_check_status_unregistered(insights_config, insights_client, _isfile):
    """
    Just check status.
        If unregistered, exit with 101 exit code (kill parent)
    """
    insights_config.return_value.load_all.return_value.status = True
    with raises(SystemExit) as exc_info:
        post_update()
    assert exc_info.value.code == 101
    insights_client.return_value.clear_local_registration.assert_not_called()
    insights_client.return_value.set_display_name.assert_not_called()


@patch("insights.client.phase.v1.isfile", side_effect=[True])
@patch("insights.client.phase.v1.get_scheduler")
@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_post_update_register_registered(insights_config, insights_client, get_scheduler, _isfile):
    """
    Client run with --register.
        If registered, exit with 0 exit code
    """
    insights_config.return_value.load_all.return_value.register = True
    with raises(SystemExit) as exc_info:
        post_update()
    assert exc_info.value.code == 0
    insights_client.return_value.get_machine_id.assert_called_once()
    insights_client.return_value.clear_local_registration.assert_not_called()
    insights_client.return_value.set_display_name.assert_not_called()
    get_scheduler.return_value.schedule.assert_called_once()


TEMP_TEST_REG_DIR = "/tmp/insights-client-registration"


@contextmanager
def _mock_no_register_files_machineid_present():
    # mock a directory with the fresh install files
    if not os.path.exists(TEMP_TEST_REG_DIR):
        os.mkdir(TEMP_TEST_REG_DIR)
    try:
        machine_id_path = os.path.join(TEMP_TEST_REG_DIR, "machine-id")
        with open(machine_id_path, "w") as machine_id_file:
            machine_id_file.write("id")
        yield
    finally:
        rmtree(TEMP_TEST_REG_DIR)


@patch('insights.client.utilities.constants.machine_id_file',
       TEMP_TEST_REG_DIR + '/machine-id')
@patch("insights.client.phase.v1.get_scheduler")
@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_post_update_register_machineid(insights_config, insights_client, get_scheduler):
    """
    Client run with --register.
        If machine-id found, exit with 0 exit code (don't kill parent)
        Also enable scheduling.
    """
    insights_config.return_value.load_all.return_value.register = True
    with _mock_no_register_files_machineid_present():
        with raises(SystemExit) as exc_info:
            post_update()
    assert exc_info.value.code == 0
    insights_client.return_value.clear_local_registration.assert_not_called()
    insights_client.return_value.set_display_name.assert_not_called()
    get_scheduler.return_value.schedule.assert_called_once()


@contextmanager
def _mock_no_machineid_present():
    # mock a directory with the fresh install files
    if not os.path.exists(TEMP_TEST_REG_DIR):
        os.mkdir(TEMP_TEST_REG_DIR)
    try:
        yield
    finally:
        rmtree(TEMP_TEST_REG_DIR)


@patch('insights.client.utilities.constants.machine_id_file',
       TEMP_TEST_REG_DIR + '/machine-id')
@patch("insights.client.phase.v1.get_scheduler")
@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_post_update_register_unregistered(insights_config, insights_client, get_scheduler):
    """
    Client run with --register.
        If unregistered, exit with 0 exit code (don't kill parent)
        Also enable scheduling.
    """
    insights_config.return_value.load_all.return_value.register = True
    with _mock_no_machineid_present():
        with raises(SystemExit) as exc_info:
            post_update()
    assert exc_info.value.code == 0
    insights_client.return_value.get_machine_id.assert_called_once()
    insights_client.return_value.clear_local_registration.assert_not_called()
    insights_client.return_value.set_display_name.assert_not_called()
    get_scheduler.return_value.schedule.assert_called_once()


@patch("insights.client.phase.v1.isfile", side_effect=[True])
@patch("insights.client.phase.v1.get_scheduler")
@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_post_update_unregister_registered(insights_config, insights_client, get_scheduler, _isfile):
    """
    Client run with --unregister.
        If registered, exit with 100 exit code
        Also disable scheduling.
    """
    insights_config.return_value.load_all.return_value.unregister = True
    insights_client.return_value.unregister = MagicMock(return_value=True)
    with raises(SystemExit) as exc_info:
        post_update()
    assert exc_info.value.code == 100
    insights_client.return_value.unregister.assert_called_once()
    insights_client.return_value.clear_local_registration.assert_not_called()
    insights_client.return_value.set_display_name.assert_not_called()
    get_scheduler.return_value.remove_scheduling.assert_called_once()


@patch("insights.client.phase.v1.isfile", side_effect=[False])
@patch("insights.client.phase.v1.get_scheduler")
@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_post_update_unregister_unregistered(insights_config, insights_client, get_scheduler, _isfile):
    """
    Client run with --unregister.
        If unregistered, exit with 101 exit code
    """
    insights_config.return_value.load_all.return_value.unregister = True
    insights_client.return_value.unregister = MagicMock(return_value=False)
    with raises(SystemExit) as exc_info:
        post_update()
    assert exc_info.value.code == 101
    insights_client.return_value.unregister.assert_called_once()
    insights_client.return_value.clear_local_registration.assert_not_called()
    insights_client.return_value.set_display_name.assert_not_called()
    get_scheduler.return_value.remove_scheduling.assert_not_called()


@patch("insights.client.phase.v1.isfile", side_effect=[False])
@patch("insights.client.phase.v1.get_scheduler")
@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_post_update_set_display_name_cli_no_register_unreg(insights_config, insights_client, get_scheduler, _isfile):
    """
    Client is unregistered, and run with --display-name but not --register
        Should exit with code 101 after registration check
    """
    insights_config.return_value.load_all.return_value.display_name = True
    insights_config.return_value.load_all.return_value._cli_opts = ['display_name']
    with raises(SystemExit) as exc_info:
        post_update()
    assert exc_info.value.code == 101
    insights_client.return_value.set_display_name.assert_not_called()
    get_scheduler.return_value.schedule.assert_not_called()


@patch("insights.client.phase.v1.isfile", side_effect=[True])
@patch("insights.client.phase.v1.get_scheduler")
@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_post_update_set_display_name_cli_no_register_reg(insights_config, insights_client, get_scheduler, _isfile):
    """
    Client is registered, and run with --display-name but not --register
        Should exit with code 100 after setting display name
    """
    insights_config.return_value.load_all.return_value.display_name = True
    insights_config.return_value.load_all.return_value._cli_opts = ['display_name']
    with raises(SystemExit) as exc_info:
        post_update()
    assert exc_info.value.code == 100
    insights_client.return_value.set_display_name.assert_called_once()
    get_scheduler.return_value.schedule.assert_not_called()


@patch("insights.client.phase.v1.isfile", side_effect=[False, False])
@patch("insights.client.phase.v1.get_scheduler")
@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_post_update_set_display_name_cli_register(insights_config, insights_client, get_scheduler, _isfile):
    """
    Client is and run with --display-name and --register
        Should set schedule and exit with code 0
        Display name is not explicitly set here
    """
    insights_config.return_value.load_all.return_value.register = True
    with raises(SystemExit) as exc_info:
        post_update()
    assert exc_info.value.code == 0
    insights_client.return_value.get_machine_id.assert_called_once()
    insights_client.return_value.set_display_name.assert_not_called()
    get_scheduler.return_value.schedule.assert_called_once()


@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_post_update_offline(insights_config, insights_client):
    """
    Offline mode short circuits this phase
    """
    insights_config.return_value.load_all.return_value.offline = True
    try:
        post_update()
    except SystemExit:
        pass
    insights_client.return_value.get_machine_id.assert_called_once()
    insights_client.return_value.clear_local_registration.assert_not_called()
    insights_client.return_value.set_display_name.assert_not_called()


@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_post_update_no_upload(insights_config, insights_client):
    """
    No-upload short circuits this phase
    """
    insights_config.return_value.load_all.return_value.no_upload = True
    try:
        post_update()
    except SystemExit:
        pass
    insights_client.return_value.get_machine_id.assert_called_once()
    insights_client.return_value.clear_local_registration.assert_not_called()
    insights_client.return_value.set_display_name.assert_not_called()


@patch("insights.client.phase.v1.isfile", side_effect=[True])
@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
# @patch("insights.client.phase.v1.InsightsClient")
def test_exit_ok(insights_config, insights_client, _isfile):
    """
    Support collection replaces the normal client run.
    """
    with raises(SystemExit) as exc_info:
        post_update()
    assert exc_info.value.code == 0
