import requests
import json
from insights.client.connection import InsightsConnection
from mock.mock import MagicMock, Mock, patch


@patch("insights.client.connection.generate_machine_id", return_value='xxxxxx')
@patch("insights.client.connection.machine_id_exists", return_value=True)
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_registration_check_ok_reg(get_proxies, _init_session, _machine_id_exists, _generate_machine_id):
    '''
    Request completed OK, registered
        Returns True
    '''
    config = Mock(legacy_upload=True, base_url='example.com')
    conn = InsightsConnection(config)

    res = requests.Response()
    res._content = json.dumps({'unregistered_at': None})
    res.status_code = 200

    conn.get = MagicMock(return_value=res)
    assert conn.api_registration_check()


@patch("insights.client.connection.generate_machine_id", return_value="12345678-abcd-efgh-ijkl-mnopqstvwxyz")
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
@patch("insights.client.connection.InsightsConnection.create_system")
def test_register_ok_reg_group(mock_create_system, _get_proxies, _init_session, _generate_machine_id):
    """
    Test the case, when we try to add system to existing group
    """

    # Mock creating connection
    config = Mock(
        legacy_upload=True,
        base_url="example.com",
        group="my_testing_group_name",
    )
    conn = InsightsConnection(config)

    # Mock creating system on the server
    mock_create_system.return_value = Mock(status_code=200)

    # Mock getting list of groups
    get_groups_res = requests.Response()
    group_list = {
        "count": 1,
        "page": 1,
        "per_page": 1,
        "total": 1,
        "results": [
            {
                "created": "2024-06-20T15:39:54.888Z",
                "id": "87654321-dcba-efgh-ijkl-123456789abc",
                "name": "my_testing_group_name",
                "org_id": "000102",
                "updated": "2024-06-20T15:39:54.888Z",
                "host_count": 0
            },
        ]
    }
    get_groups_res.encoding = "utf-8"
    get_groups_res._content = json.dumps(group_list).encode("utf-8")
    get_groups_res.status_code = 200
    conn.get = MagicMock(return_value=get_groups_res)

    # Mock putting system to the group
    updated_group = {
        "created": "2024-06-21T10:32:27.135Z",
        "id": "bA6deCFc19564430AB814bf8F70E8cEf",
        "name": "my_testing_group_name",
        "org_id": "000102",
        "updated": "2024-06-21T10:32:27.135Z",
        "host_count": 1
    }
    post_system_to_group_res = requests.Response()
    post_system_to_group_res.encoding = "utf-8"
    post_system_to_group_res._content = json.dumps(updated_group).encode("utf-8")
    post_system_to_group_res.status_code = 201
    conn.post = MagicMock(return_value=post_system_to_group_res)

    # Test the ^%&$#@* code
    _, _, group_name, _ = conn.register()
    assert group_name == "my_testing_group_name"


@patch("insights.client.connection.generate_machine_id", return_value="12345678-abcd-efgh-ijkl-mnopqstvwxyz")
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
@patch("insights.client.connection.InsightsConnection.create_system")
def test_register_ok_reg_empty_group(mock_create_system, _get_proxies, _init_session, _generate_machine_id):
    """
    Test the case, when we try to add system to group that does not exist,
    but server response with empty list and not 404 code
    """

    # Mock creating connection
    config = Mock(
        legacy_upload=True,
        base_url="example.com",
        group="my_testing_group_name",
    )
    conn = InsightsConnection(config)

    # Mock creating system on the server
    mock_create_system.return_value = Mock(status_code=200)

    # Mock getting the list of groups
    get_groups_res = requests.Response()
    group_list = {
        "count": 0,
        "page": 0,
        "per_page": 0,
        "total": 0,
        "results": []
    }
    get_groups_res.encoding = "utf-8"
    get_groups_res._content = json.dumps(group_list).encode("utf-8")
    get_groups_res.status_code = 200
    conn.get = MagicMock(return_value=get_groups_res)

    # Mock response of creating new group with new system
    new_group = {
        "created": "2024-06-21T12:25:21.009Z",
        "id": "bA6deCFc19564430AB814bf8F70E8cEf",
        "name": "my_testing_group_name",
        "org_id": "000102",
        "updated": "2024-06-21T12:25:21.009Z",
        "host_count": 1
    }
    post_system_to_group_res = requests.Response()
    post_system_to_group_res.encoding = "utf-8"
    post_system_to_group_res._content = json.dumps(new_group).encode("utf-8")
    post_system_to_group_res.status_code = 201
    conn.post = MagicMock(return_value=post_system_to_group_res)

    # Test the code
    _, _, group_name, _ = conn.register()
    assert group_name == "my_testing_group_name"


@patch("insights.client.connection.generate_machine_id", return_value="12345678-abcd-efgh-ijkl-mnopqstvwxyz")
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
@patch("insights.client.connection.InsightsConnection.create_system")
def test_register_ok_reg_non_existing_group(mock_create_system, _get_proxies, _init_session, _generate_machine_id):
    """
    Test the case, when we try to add the system to a group that has not been already created,
    and it is necessary to create the group during registration process.
    """

    # Mock creating connection
    config = Mock(
        legacy_upload=True,
        base_url="example.com",
        group="my_testing_group_name",
    )
    conn = InsightsConnection(config)

    # Mock creating system on the server
    mock_create_system.return_value = Mock(status_code=200)

    # Mock getting list of groups
    get_groups_res = requests.Response()
    get_groups_res.encoding = "utf-8"
    get_groups_res.status_code = 404
    conn.get = MagicMock(return_value=get_groups_res)

    # Mock response of creating new group with new system
    new_group = {
        "created": "2024-06-21T12:25:21.009Z",
        "id": "bA6deCFc19564430AB814bf8F70E8cEf",
        "name": "my_testing_group_name",
        "org_id": "000102",
        "updated": "2024-06-21T12:25:21.009Z",
        "host_count": 1
    }
    post_system_to_group_res = requests.Response()
    post_system_to_group_res.encoding = "utf-8"
    post_system_to_group_res._content = json.dumps(new_group).encode("utf-8")
    post_system_to_group_res.status_code = 201
    conn.post = MagicMock(return_value=post_system_to_group_res)

    # Test the code
    _, _, group_name, _ = conn.register()
    assert group_name == "my_testing_group_name"


@patch("insights.client.connection.generate_machine_id", return_value="12345678-abcd-efgh-ijkl-mnopqstvwxyz")
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
@patch("insights.client.connection.InsightsConnection.create_system")
def test_register_failed_reg_non_existing_group(mock_create_system, _get_proxies, _init_session, _generate_machine_id):
    """
    Test the case, when we try to add the system to a group that has not been already created,
    but it is not possible to create the group during registration process.
    """

    # Mock creating connection
    config = Mock(
        legacy_upload=True,
        base_url="example.com",
        group="my_testing_group_name",
    )
    conn = InsightsConnection(config)

    # Mock creating system on the server
    mock_create_system.return_value = Mock(status_code=200)

    # Mock getting list of groups
    get_groups_res = requests.Response()
    get_groups_res.encoding = "utf-8"
    get_groups_res.status_code = 404
    conn.get = MagicMock(return_value=get_groups_res)

    # Mock response of not creating new group due to lack of permissions
    post_system_to_group_res = requests.Response()
    post_system_to_group_res.encoding = "utf-8"
    post_system_to_group_res.status_code = 403
    conn.post = MagicMock(return_value=post_system_to_group_res)

    # Test the code
    _, _, group_name, _ = conn.register()
    assert group_name == "my_testing_group_name"


@patch("insights.client.connection.generate_machine_id", return_value='xxxxxx')
@patch("insights.client.connection.machine_id_exists", return_value=True)
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_registration_check_ok_reg_then_unreg(get_proxies, _init_session, _machine_id_exists, _generate_machine_id):
    '''
    Request completed OK, was once registered but has been unregistered
        Returns the date it was unregistered
    '''
    config = Mock(legacy_upload=True, base_url='example.com')
    conn = InsightsConnection(config)

    res = requests.Response()
    res._content = json.dumps({'unregistered_at': '2019-04-10'})
    res.status_code = 200

    conn.get = MagicMock(return_value=res)
    assert conn.api_registration_check() == '2019-04-10'


@patch("insights.client.connection.machine_id_exists", return_value=True)
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_registration_check_ok_unreg(get_proxies, _init_session, _machine_id_exists):
    '''
    Request completed OK, has never been registered
        Returns None
    '''
    config = Mock(legacy_upload=True, base_url='example.com')
    conn = InsightsConnection(config)

    res = requests.Response()
    res._content = json.dumps({})
    res.status_code = 404

    conn.get = MagicMock(return_value=res)
    assert conn.api_registration_check() is None


@patch("insights.client.connection.generate_machine_id", return_value='xxxxxx')
@patch("insights.client.connection.machine_id_exists", return_value=True)
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_registration_check_bad_res(get_proxies, _init_session, _machine_id_exists, _generate_machine_id):
    '''
    Can't parse response
        Returns False
    '''
    config = Mock(legacy_upload=True, base_url='example.com')
    conn = InsightsConnection(config)

    res = requests.Response()
    res._content = 'zSDFasfghsRGH'
    res.status_code = 500

    conn.get = MagicMock(return_value=res)
    assert conn.api_registration_check() is False


@patch("insights.client.connection.generate_machine_id", return_value='xxxxxx')
@patch("insights.client.connection.machine_id_exists", return_value=True)
@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
@patch("insights.client.connection.InsightsConnection.test_connection")
def test_registration_check_conn_error(test_connection, get_proxies, _init_session, _machine_id_exists, _generate_machine_id):
    '''
    Can't connect, run connection test
        Returns False
    '''
    config = Mock(legacy_upload=True, base_url='example.com')
    conn = InsightsConnection(config)

    conn.get = MagicMock()
    conn.get.side_effect = requests.ConnectionError()
    assert conn.api_registration_check() is False
    test_connection.assert_called_once()
