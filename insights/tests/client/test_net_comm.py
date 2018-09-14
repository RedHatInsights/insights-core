# -*- coding: utf-8 -*-

from insights.client.phase import v1
from insights.tests.helpers import dummy_requests_session, getenv_bool, Timeout
from mock.mock import patch
from pytest import mark


RUN_TESTS = getenv_bool("TEST_NET_COMM", False)
MAX_TIME = 30  # The tests mustn't run longer even if all requests wait for timeout.


def load_all(self):
    return self


@mark.skipif(not RUN_TESTS, reason="Net communication tests take a long time to finish.")
@patch("insights.client.connection.requests.Session", dummy_requests_session)
@patch("insights.client.config.InsightsConfig.load_all", load_all)
def test_failure_does_not_take_too_long():
    """
    Client execution does not take too long if connection is blocked by a firewall. First thing that fails is the new
    egg fetch in the update phase. Every net request up to this point must timeout in reasonable time.
    """
    def worker():
        """
        Runs first two phases. Expected to be run in a subprocess. The update phase is expected to fail.
        """
        try:
            v1.pre_update()
        except SystemExit as exception:
            if exception.code:
                exit(1)  # This phase must not fail.
        else:
            exit(1)  # Phase did not exit.

        try:
            v1.update()
        except SystemExit as exception:
            if exception.code != 1:
                exit(1)  # Egg update is expected to fail.
        else:
            exit(1)  # Phase did not exit.

    timeout = Timeout()
    timeout.start(worker, MAX_TIME)

    assert timeout.state != timeout.FAIL
    assert timeout.state != timeout.TIMEOUT
    assert timeout.state == timeout.SUCCESS
