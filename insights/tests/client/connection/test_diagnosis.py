import requests
from insights.client import InsightsClient
from insights.client.config import InsightsConfig
from insights.client.connection import InsightsConnection
from mock.mock import patch, Mock

TEST_REMEDIATION_ID = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
TEST_MACHINE_ID = 'yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy'


@patch('insights.client.connection.InsightsConnection._init_session', Mock())
@patch('insights.client.connection.InsightsConnection.get_proxies', Mock())
@patch('insights.client.connection.generate_machine_id', Mock(return_value=TEST_MACHINE_ID))
def test_get_diagnosis():
    '''
    Verify that get_diagnosis returns a dict of response data on 200
    and None on failure codes

    Verify that no remediation ID is passed
    '''
    conf = InsightsConfig()
    c = InsightsConnection(conf)

    res = requests.Response()
    c.get = Mock(return_value=res)

    # OK
    res.status_code = 200
    res._content = b"{\"test\": \"test\"}"
    assert c.get_diagnosis() == {"test": "test"}
    c.get.assert_called_with('https://' + conf.base_url + '/remediations/v1/diagnosis/' + TEST_MACHINE_ID, params={})

    # not found
    res.status_code = 404
    assert c.get_diagnosis() is None
    c.get.assert_called_with('https://' + conf.base_url + '/remediations/v1/diagnosis/' + TEST_MACHINE_ID, params={})

    # server error
    res.status_code = 500
    assert c.get_diagnosis() is None
    c.get.assert_called_with('https://' + conf.base_url + '/remediations/v1/diagnosis/' + TEST_MACHINE_ID, params={})


@patch('insights.client.connection.InsightsConnection._init_session', Mock())
@patch('insights.client.connection.InsightsConnection.get_proxies', Mock())
@patch('insights.client.connection.generate_machine_id', Mock(return_value=TEST_MACHINE_ID))
def test_get_diagnosis_with_id():
    '''
    Verify that get_diagnosis returns a dict of response data on 200
    and None on failure codes

    Verify that the remediation ID is passed
    '''
    conf = InsightsConfig()
    c = InsightsConnection(conf)

    res = requests.Response()
    c.get = Mock(return_value=res)

    # OK
    res.status_code = 200
    res._content = b"{\"test\": \"test\"}"
    assert c.get_diagnosis(TEST_REMEDIATION_ID) == {"test": "test"}
    c.get.assert_called_with('https://' + conf.base_url + '/remediations/v1/diagnosis/' + TEST_MACHINE_ID, params={'remediation': TEST_REMEDIATION_ID})

    # not found
    res.status_code = 404
    assert c.get_diagnosis(TEST_REMEDIATION_ID) is None
    c.get.assert_called_with('https://' + conf.base_url + '/remediations/v1/diagnosis/' + TEST_MACHINE_ID, params={'remediation': TEST_REMEDIATION_ID})

    # server error
    res.status_code = 500
    assert c.get_diagnosis(TEST_REMEDIATION_ID) is None
    c.get.assert_called_with('https://' + conf.base_url + '/remediations/v1/diagnosis/' + TEST_MACHINE_ID, params={'remediation': TEST_REMEDIATION_ID})


def test_get_diagnosis_offline():
    conf = InsightsConfig()
    conf.offline = True
    c = InsightsClient(conf)
    assert c.get_diagnosis() is None
