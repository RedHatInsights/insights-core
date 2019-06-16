#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from insights.core.context import OSP
from insights.parsers.rabbitmq import RabbitMQUsers
from insights.tests import context_wrap

osp_controller = OSP()
osp_controller.role = "Controller"

RABBITMQ_LIST_USERS = """
Listing users ...
guest   [administrator]
test    [administrator]
...done.
"""

RABBITMQ_LIST_EDGES = '''
Listing users ...
probe   []
brain   []
none
user1   [monitoring,user]
guest   [made up data]
...done.
'''


def test_rabbitmq_list_users():
    context = context_wrap(RABBITMQ_LIST_USERS, hostname="controller_1", osp=osp_controller)
    result = RabbitMQUsers(context)
    expect = {"guest": "administrator", "test": "administrator"}
    assert result.data == expect


def test_rabbitmq_list_users_stub():
    context = context_wrap(RABBITMQ_LIST_EDGES, hostname="controller_1", osp=osp_controller)
    result = RabbitMQUsers(context)
    assert result.data['probe'] == ''
    assert 'none' not in result.data
    assert result.data['user1'] == 'monitoring,user'
    assert result.data['guest'] == 'made up data'
