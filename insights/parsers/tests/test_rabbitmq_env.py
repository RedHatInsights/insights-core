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

import doctest

from .test_rabbitmq_queues import QUEUES
from insights.parsers import rabbitmq
from insights.tests import context_wrap


RABBITMQ_ENV = """
RABBITMQ_SERVER_ERL_ARGS="+K true +P 1048576 -kernel inet_default_connect_options [{nodelay,true},{raw,6,18,<<5000:64/native>>}] -kernel inet_default_listen_options [{raw,6,18,<<5000:64/native>>}]"
""".strip()

RABBITMQ_ENV_DIFFERENT_TIMEOUT = """
RABBITMQ_SERVER_ERL_ARGS="+K true +P 1048576 -kernel inet_default_connect_options [{nodelay,true},{raw,6,18,<<5000:64/native>>}] -kernel inet_default_listen_options [{raw,6,18,<<3000:64/native>>}]"
""".strip()

RABBITMQ_ENV_OPTIONS = """
OPTIONS="+K true +P 1048576 -kernel inet_default_connect_options [{nodelay,true},{raw,6,18,<<5000:64/native>>}] -kernel inet_default_listen_options [{raw,6,18,<<5000:64/native>>}]"
""".strip()

RABBITMQ_ENV_BAD_PATTERN = """
RABBITMQ_SERVER_ERL_ARGS="+K true +P 1048576 -kernel inet_default_connect_options [{nodelay,true},{raw,6,18,<<5000:64/native>>}] -kernel inet_default_options [{raw,6,18,<<5000:64/native>>}]"
""".strip()


def test_rabbitmq_env():
    rabbitmq_env = rabbitmq.RabbitMQEnv(context_wrap(RABBITMQ_ENV))
    assert rabbitmq_env.rabbitmq_server_erl_args == '+K true +P 1048576 -kernel inet_default_connect_options [{nodelay,true},{raw,6,18,<<5000:64/native>>}] -kernel inet_default_listen_options [{raw,6,18,<<5000:64/native>>}]'
    assert rabbitmq_env.data['RABBITMQ_SERVER_ERL_ARGS'] == '+K true +P 1048576 -kernel inet_default_connect_options [{nodelay,true},{raw,6,18,<<5000:64/native>>}] -kernel inet_default_listen_options [{raw,6,18,<<5000:64/native>>}]'
    assert rabbitmq_env.rmq_erl_tcp_timeout == '5000'

    rabbitmq_env = rabbitmq.RabbitMQEnv(context_wrap(RABBITMQ_ENV_DIFFERENT_TIMEOUT))
    assert rabbitmq_env.rmq_erl_tcp_timeout is None

    rabbitmq_env = rabbitmq.RabbitMQEnv(context_wrap(RABBITMQ_ENV_OPTIONS))
    assert rabbitmq_env.rabbitmq_server_erl_args is None
    assert rabbitmq_env.rmq_erl_tcp_timeout is None

    rabbitmq_env = rabbitmq.RabbitMQEnv(context_wrap(RABBITMQ_ENV_BAD_PATTERN))
    assert rabbitmq_env.rmq_erl_tcp_timeout is None


def test_doc_examples():
    failed, total = doctest.testmod(
        rabbitmq,
        globs={'rabbitmq_env': rabbitmq.RabbitMQEnv(context_wrap(RABBITMQ_ENV)),
               'queues': rabbitmq.RabbitMQQueues(context_wrap(QUEUES))}
    )
    assert failed == 0
