from falafel.core.context import OSP
from falafel.mappers.rabbitmq import RabbitMQUsers
from falafel.tests import context_wrap

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
    result = RabbitMQUsers.parse_context(context)
    expect = {"guest": "administrator", "test": "administrator"}
    assert result.data == expect
