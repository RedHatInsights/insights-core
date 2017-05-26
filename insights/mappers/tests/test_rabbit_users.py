from insights.core.context import OSP
from insights.mappers.rabbitmq import RabbitMQUsers
from insights.tests import context_wrap

osp_controller = OSP()
osp_controller.role = "Controller"

RABBITMQ_LIST_USERS = """
Listing users ...
guest   [administrator]
test    [administrator]
...done.
"""


def test_rabbitmq_list_users():
    context = context_wrap(RABBITMQ_LIST_USERS, hostname="controller_1", osp=osp_controller)
    result = RabbitMQUsers(context)
    expect = {"guest": "administrator", "test": "administrator"}
    assert result.data == expect
