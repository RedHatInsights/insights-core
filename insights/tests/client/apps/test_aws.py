import json
from requests import ConnectionError, Timeout
from requests.exceptions import HTTPError
from ssl import SSLError
from urllib3.exceptions import MaxRetryError
from mock.mock import patch, Mock
from insights.client.config import InsightsConfig
from insights.client.connection import InsightsConnection
from insights.client.apps import aws


@patch('insights.client.apps.aws.get_aws_identity')
@patch('insights.client.apps.aws.post_to_hydra')
@patch('insights.client.apps.aws.enable_delayed_registration')
def test_aws_main(enable_delayed_registration, post_to_hydra, get_aws_identity):
    '''
    Test the flow of the main routine for success and failure
    '''
    # portal access with insights registration
    conf = InsightsConfig(portal_access=True)
    assert aws.aws_main(conf)
    get_aws_identity.assert_called_once()
    post_to_hydra.assert_called_once()
    enable_delayed_registration.assert_called_once()

    get_aws_identity.reset_mock()
    post_to_hydra.reset_mock()
    enable_delayed_registration.reset_mock()

    # portal access, no insights registration
    conf = InsightsConfig(portal_access_no_insights=True)
    assert aws.aws_main(conf)
    get_aws_identity.assert_called_once()
    post_to_hydra.assert_called_once()
    enable_delayed_registration.assert_not_called()

    get_aws_identity.reset_mock()
    post_to_hydra.reset_mock()
    enable_delayed_registration.reset_mock()

    # identity call fails - returns false
    conf = InsightsConfig(portal_access=True)
    get_aws_identity.return_value = None
    result = aws.aws_main(conf)
    assert not result
    post_to_hydra.assert_not_called()
    enable_delayed_registration.assert_not_called()

    get_aws_identity.reset_mock()
    post_to_hydra.reset_mock()
    enable_delayed_registration.reset_mock()

    # hydra call fails - returns false
    conf = InsightsConfig(portal_access=True)
    post_to_hydra.return_value = False
    result = aws.aws_main(conf)
    assert not result
    enable_delayed_registration.assert_not_called()


def test_get_uri():
    '''
    Test that GET success and failure handled properly
    '''
    pass


@patch('insights.client.apps.aws.get_uri')
def test_get_aws_identity(get_uri):
    '''
    Test that AWS identity success and failure handled properly
    '''
    # returns OK
    get_uri.side_effect = [Mock(ok=True, content=b'{"test": "test"}'), Mock(ok=True, content="test")]
    conn = InsightsConnection(InsightsConfig())
    assert aws.get_aws_identity(conn)

    # URIs don't return OK status, return None
    get_uri.side_effect = [Mock(ok=False, content=None), Mock(ok=False, content=None)]
    assert aws.get_aws_identity(conn) is None


@patch('insights.client.apps.aws.logger.error')
def test_post_to_hydra(logger_error):
    '''
    Test that POST to Hydra success and failure handled properly
    '''
    conn = InsightsConnection(InsightsConfig())
    error_msg = '{"message":"error", "detailMessage":"error details"}'
    error_json = json.loads(error_msg)
    # successful POST
    conn.session.post = Mock(return_value=Mock(status_code=200))
    assert aws.post_to_hydra(conn, '')
    conn.session.post.assert_called_once()

    # connection error
    conn.session.post = Mock(side_effect=(ConnectionError, Timeout, SSLError, MaxRetryError))
    assert not aws.post_to_hydra(conn, '')
    conn.session.post.assert_called_once()

    # bad response w/ JSON
    conn.session.post = Mock(
        return_value=Mock(status_code=500,
                          text=error_msg,
                          json=Mock(return_value=error_json),
                          raise_for_status=Mock(return_value='', side_effect=HTTPError)))
    assert not aws.post_to_hydra(conn, '')
    conn.session.post.assert_called_once()
    logger_error.assert_called_with('%s\n%s', 'error', 'error details')

    # bad response w/ no JSON
    conn.session.post = Mock(
        return_value=Mock(status_code=500,
                          text='',
                          json=Mock(side_effect=ValueError),
                          raise_for_status=Mock(return_value='', side_effect=HTTPError)))
    assert not aws.post_to_hydra(conn, '')
    conn.session.post.assert_called_once()
    logger_error.assert_called_with('Could not parse JSON response.')
