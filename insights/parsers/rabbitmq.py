"""
Parsers for RabbitMQ
====================

Parsers included in this module are:

RabbitMQUsers - command ``/usr/sbin/rabbitmqctl list_users``
------------------------------------------------------------

RabbitMQQueues - command ``/usr/sbin/rabbitmqctl list_queues name messages consumers auto_delete``
--------------------------------------------------------------------------------------------------

RabbitMQEnv - file ``/etc/rabbitmq/rabbitmq-env.conf``
------------------------------------------------------
"""
from collections import namedtuple
from re import compile

from insights.core import CommandParser, SysconfigOptions
from insights.core.exceptions import ParseException
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.rabbitmq_users)
class RabbitMQUsers(CommandParser):

    def parse_content(self, content):
        self.data = {}
        for line in content[1:-1]:
            line_splits = line.split(None, 1)
            if len(line_splits) > 1:
                self.data[line_splits[0]] = line_splits[1][1:-1]


TRUE_FALSE = {'true': True, 'false': False}
"""dict: Dictionary for converting true/false strings to bool."""


@parser(Specs.rabbitmq_queues)
class RabbitMQQueues(CommandParser):
    """Parse the output of the `rabbitmqctl list_queues` command.

    The actual command is
    `rabbitmqctl list_queues name messages consumers auto_delete`.

    The four columns that are output are:

    1. name - The name of the queue with non-ASCII characters escaped as in C.
    2. messages - Sum of ready and unacknowledged messages (queue depth).
    3. consumers - Number of consumers.
    4. auto_delete - Whether the queue will be deleted automatically when no longer used.

    The output of the command looks like::

        cinder-scheduler        0       3       false
        cinder-scheduler.ha-controller  0       3       false
        cinder-scheduler_fanout_ea9c69fb630f41b2ae6120eba3cd43e0        8141    1   true
        cinder-scheduler_fanout_9aed9fbc3d4249289f2cb5ea04c062ab        8145    0   true
        cinder-scheduler_fanout_b7a2e488f3ed4e1587b959f9ac255b93        8141    0   true

    Examples:

        >>> queues.data[0]
        QueueInfo(name='cinder-scheduler', messages=0, consumers=3, auto_delete=False)
        >>> queues.data[0].name
        'cinder-scheduler'
        >>> queues.data[1].name
        'cinder-scheduler.ha-controller'

    Raises:
        ParseException: Raised if the data indicates an error in acquisition or if
            the auto_delete value is not true or false.
        ValueError: Raised if any of the numbers are not valid numbers
    """

    QueueInfo = namedtuple('QueueInfo', ['name', 'messages', 'consumers', 'auto_delete'])
    """namedtuple: Structure to hold a line of RabbitMQ queue information."""

    def parse_content(self, content):
        self.data = []
        for line in content:
            if "Listing queues ..." in line:
                continue
            if "...done." in line:
                continue
            parts = line.split()
            if len(parts) == 4 and not line.startswith('Error:'):
                if parts[3].lower() in TRUE_FALSE:
                    self.data.append(RabbitMQQueues.QueueInfo(
                        parts[0], int(parts[1]), int(parts[2]),
                        TRUE_FALSE[parts[3].lower()])
                    )
                else:
                    raise ParseException(
                        "auto_delete should be true or false: {0}".format(line))
            else:
                raise ParseException("Data appears invalid: {0}".format(line))


@parser(Specs.rabbitmq_env)
class RabbitMQEnv(SysconfigOptions):
    """Parse the content of file ``/etc/rabbitmq/rabbitmq-env.conf`` using
    the ``SysconfigOptions`` base class.


    Sample content of the file ``/etc/rabbitmq/rabbitmq-env.conf``::

        RABBITMQ_SERVER_ERL_ARGS="+K true +P 1048576 -kernel inet_default_connect_options [{nodelay,true},{raw,6,18,<<5000:64/native>>}] -kernel inet_default_listen_options [{raw,6,18,<<5000:64/native>>}]"

    Example:

        >>> rabbitmq_env.rabbitmq_server_erl_args
        '+K true +P 1048576 -kernel inet_default_connect_options [{nodelay,true},{raw,6,18,<<5000:64/native>>}] -kernel inet_default_listen_options [{raw,6,18,<<5000:64/native>>}]'
        >>> rabbitmq_env.data['RABBITMQ_SERVER_ERL_ARGS']
        '+K true +P 1048576 -kernel inet_default_connect_options [{nodelay,true},{raw,6,18,<<5000:64/native>>}] -kernel inet_default_listen_options [{raw,6,18,<<5000:64/native>>}]'
        >>> rabbitmq_env.rmq_erl_tcp_timeout
        '5000'

    Attributes:
        rabbitmq_server_erl_args(str): If RABBITMQ_SERVER_ERL_ARGS otherwise ``None``.

        rmq_erl_tcp_timeout(str): If value of inet_default_connect_options equals value of inet_default_listen_options. Otherwise ``None``.
    """
    @property
    def rabbitmq_server_erl_args(self):
        return self.data.get('RABBITMQ_SERVER_ERL_ARGS', None)

    @property
    def rmq_erl_tcp_timeout(self):
        pattern_connect_options = compile(r"inet_default_connect_options.*?\<<([0-9]*)\:64")
        pattern_listen_options = compile(r"inet_default_listen_options.*?\<<([0-9]*)\:64")

        if self.rabbitmq_server_erl_args:
            if pattern_connect_options.search(self.rabbitmq_server_erl_args) and pattern_listen_options.search(self.rabbitmq_server_erl_args):
                connect_timeout = pattern_connect_options.findall(self.rabbitmq_server_erl_args)[0]
                listen_timeout = pattern_listen_options.findall(self.rabbitmq_server_erl_args)[0]
                if connect_timeout == listen_timeout:
                    return connect_timeout
