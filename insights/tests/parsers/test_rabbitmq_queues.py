import pytest
from insights.parsers import ParseException
from insights.parsers.rabbitmq import RabbitMQQueues
from insights.tests import context_wrap

QUEUES = """
cinder-scheduler        0       3       false
cinder-scheduler.ha-controller  0       3       false
cinder-scheduler_fanout_ea9c69fb630f41b2ae6120eba3cd43e0        8141    1   true
cinder-scheduler_fanout_9aed9fbc3d4249289f2cb5ea04c062ab        8145    0   true
cinder-scheduler_fanout_b7a2e488f3ed4e1587b959f9ac255b93        8141    0   true
"""

MORE_QUEUES = """
Listing queues ...
q-agent-notifier-tunnel-delete_fanout_a8dc17bbb6ee469c8aaab31079c01c1c	0	1	false
dhcp_agent.undercloud-per720xd.default.redhat.local	0	1	false
mistral_executor.0.0.0.0	0	1	false
reply_aeff2b095dac4b09b8a4ea27986b402c	0	1	false
reply_6cf2931b774f4a58a14c819570059114	0	1	false
q-agent-notifier-tunnel-update	0	1	false
cert	0	1	false
q-plugin.undercloud-per720xd.default.redhat.local	0	2	false
reply_5d74d09f9758439fbd247097c096c1a2	0	1	false
metering.sample	1	1	false
heat-engine-listener.65218f91-59b6-45bc-99df-63f5af707351	0	1	false
reply_e7fb8381d78b4dcf9501ba8a72ad335f	0	1	false
reply_e366ce8a5b3846608e1e181e9e413231	0	1	false
reply_19ec1f054dc74298b896cbbb06c7b7e7	0	1	false
scheduler.undercloud-per720xd.default.redhat.local	0	1	false
q-server-resource-versions_fanout_56cc075fd8cc486bacd0648225b61970	0	1	false
q-server-resource-versions.undercloud-per720xd.default.redhat.local	0	2	false
mistral_engine.0.0.0.0	0	1	false
reply_c97293591c5c46be9331f0a5662f8961	0	1	false
mistral_engine_fanout_a660b93980ca41ac84b6f1b56cf8a25c	0	1	false
event.sample	0	1	false
...done.
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

    many_queues = RabbitMQQueues(context_wrap(MORE_QUEUES))
    assert many_queues.data[1].name == "dhcp_agent.undercloud-per720xd.default.redhat.local"
    assert many_queues.data[1].auto_delete is False

    with pytest.raises(ParseException):
        queues = RabbitMQQueues(context_wrap(QUEUES_BAD_1))

    with pytest.raises(ValueError):
        queues = RabbitMQQueues(context_wrap(QUEUES_BAD_2))

    with pytest.raises(ParseException):
        queues = RabbitMQQueues(context_wrap(QUEUES_BAD_3))
