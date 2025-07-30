import os
import pytest
from mock.mock import patch
from insights.client.constants import InsightsConstants as constants
from insights.client.connection import InsightsConnection
from insights.client.config import InsightsConfig


@patch("insights.client.connection.InsightsConnection._init_session")
@patch('insights.client.utilities.generate_machine_id')
@patch('insights.client.connection.InsightsConnection.get')
@patch('insights.client.connection.os.path.isfile', return_value=False)
def test_unregistered_check_results(_is_file, get, generate_machine_id, _init_session):
    config = InsightsConfig()
    connection = InsightsConnection(config)

    with pytest.raises(Exception):
        connection.get_advisor_report()

    assert not os.path.isfile(constants.registered_files[0])
    generate_machine_id.assert_not_called()
    get.assert_not_called()
