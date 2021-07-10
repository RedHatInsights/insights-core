import doctest
import pytest

from insights.parsers import satellite_missed_queues
from insights.tests import context_wrap
from insights import SkipComponent


SATELLITE_MISSED_QUEUES_OUTPUT1 = """
pulp.agent.09008eec-aba6-4174-aa9f-e930004ce5c9:2018-01-16 00:06:13
pulp.agent.fac7ebbc-ee4f-44b4-9fe0-3f4e42c7f024:2018-01-16 00:06:16
0
""".strip()

SATELLITE_MISSED_QUEUES_OUTPUT2 = """
pulp.agent.09008eec-aba6-4174-aa9f-e930004ce5c9:2018-01-16 00:06:13
pulp.agent.iac7ebbc-ee4f-44b4-9fe0-3f4e42c7f024:2018-01-16 00:06:16
pulp.agent.aac7ebbc-ee4f-44b4-9fe0-3f4e42c7f024:2018-01-16 00:06:17
pulp.agent.bac7ebbc-ee4f-44b4-9fe0-3f4e42c7f024:2018-01-16 00:06:18
pulp.agent.cac7ebbc-ee4f-44b4-9fe0-3f4e42c7f024:2018-01-16 00:06:19
pulp.agent.dac7ebbc-ee4f-44b4-9fe0-3f4e42c7f024:2018-01-16 00:06:20
pulp.agent.eac7ebbc-ee4f-44b4-9fe0-3f4e42c7f024:2018-01-16 00:06:21
pulp.agent.fac7ebbc-ee4f-44b4-9fe0-3f4e42c7f024:2018-01-16 00:06:22
pulp.agent.gac7ebbc-ee4f-44b4-9fe0-3f4e42c7f024:2018-01-16 00:06:23
pulp.agent.hac7ebbc-ee4f-44b4-9fe0-3f4e42c7f024:2018-01-16 00:06:24
1
""".strip()

SATELLITE_MISSED_QUEUES_BAD_OUTPUT_1 = """
pulp.agent.09008eec-aba6-4174-aa9f-e930004ce5c9:2018-01-16 00:06:13
""".strip()

SATELLITE_MISSED_QUEUES_BAD_OUTPUT_2 = """
abc
def
""".strip()

SATELLITE_MISSED_QUEUES_BAD_OUTPUT_3 = """
pulp.agent.eac7ebbc-ee4f-44b4-9fe0-3f4e42c7f024:2018-01-16 00:06:21
pulp.agent.fac7ebbc-ee4f-44b4-9fe0-3f4e42c7f024:2018-01-16 00:06:22
pulp.agent.gac7ebbc-ee4f-44b4-9fe0-3f4e42c7f024:2018-01-16 00:06:23
pulp.agent.hac7ebbc-ee4f-44b4-9fe0-3f4e42c7f024:2018-01-16 00:06:24
""".strip()


def test_satellite_queue():
    queues = satellite_missed_queues.SatelliteMissedQueues(context_wrap(SATELLITE_MISSED_QUEUES_OUTPUT2))
    assert queues.truncated
    assert len(queues.missed_queues) == 10
    assert 'pulp.agent.hac7ebbc-ee4f-44b4-9fe0-3f4e42c7f024' in queues.missed_queues
    assert queues.missed_queues['pulp.agent.hac7ebbc-ee4f-44b4-9fe0-3f4e42c7f024'] == '2018-01-16 00:06:24'


def test_doc_examples():
    env = {
        'satellite_queues': satellite_missed_queues.SatelliteMissedQueues(context_wrap(SATELLITE_MISSED_QUEUES_OUTPUT1)),
    }
    failed, total = doctest.testmod(satellite_missed_queues, globs=env)
    assert failed == 0


def test_exception():
    with pytest.raises(SkipComponent):
        satellite_missed_queues.SatelliteMissedQueues(context_wrap(SATELLITE_MISSED_QUEUES_BAD_OUTPUT_1))
    with pytest.raises(SkipComponent):
        satellite_missed_queues.SatelliteMissedQueues(context_wrap(SATELLITE_MISSED_QUEUES_BAD_OUTPUT_2))
    with pytest.raises(SkipComponent):
        satellite_missed_queues.SatelliteMissedQueues(context_wrap(SATELLITE_MISSED_QUEUES_BAD_OUTPUT_3))
