import pytest
from falafel.mappers import ParseException
from falafel.mappers.rabbitmq import RabbitMQQueues
from falafel.tests import context_wrap

QUEUES = """
cinder-scheduler        0       3       false
cinder-scheduler.ha-controller  0       3       false
cinder-scheduler_fanout_ea9c69fb630f41b2ae6120eba3cd43e0        8141    1   true
cinder-scheduler_fanout_9aed9fbc3d4249289f2cb5ea04c062ab        8145    0   true
cinder-scheduler_fanout_b7a2e488f3ed4e1587b959f9ac255b93        8141    0   true
"""

QUEUES_BAD_1 = """
Error: unable to connect to node
"""
QUEUES_BAD_2 = """
queue1 1 x false
"""
QUEUES_BAD_3 = """
queue1 1 1 maybe
"""


def test_rabbitmq_queues():
    queues = RabbitMQQueues(context_wrap(QUEUES))
    assert queues is not None
    assert len(queues.data) == 5
    assert queues.data[0] == RabbitMQQueues.QueueInfo(
        name="cinder-scheduler",
        messages=0,
        consumers=3,
        auto_delete=False)
    assert queues.data[3] == RabbitMQQueues.QueueInfo(
        name="cinder-scheduler_fanout_9aed9fbc3d4249289f2cb5ea04c062ab",
        messages=8145,
        consumers=0,
        auto_delete=True)
    assert queues.data[3].name == "cinder-scheduler_fanout_9aed9fbc3d4249289f2cb5ea04c062ab"

    with pytest.raises(ParseException):
        queues = RabbitMQQueues(context_wrap(QUEUES_BAD_1))

    with pytest.raises(ValueError):
        queues = RabbitMQQueues(context_wrap(QUEUES_BAD_2))

    with pytest.raises(ParseException):
        queues = RabbitMQQueues(context_wrap(QUEUES_BAD_3))
