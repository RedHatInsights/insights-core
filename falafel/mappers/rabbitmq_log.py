"""
rabbitmq_log - Files /var/log/rabbitmq...
=========================================

Module for parsing the log files for RabbitMQ

"""

from .. import LogFileOutput, mapper


@mapper("rabbitmq_startup_log")
class RabbitMQStartupLog(LogFileOutput):
    """Class for parsing ``/var/log/rabbitmq/startup_log`` file.

    Typical content of ``startup_log`` file is::

        Starting all nodes...
        Starting node rabbit@ubuntu...

        +---+   +---+
        |   |   |   |
        |   |   |   |
        |   |   |   |
        |   +---+   +-------+
        |                   |
        | RabbitMQ  +---+   |
        |           |   |   |
        |   v1.8.0  +---+   |
        |                   |
        +-------------------+
        AMQP 8-0
        Copyright (C) 2007-2010 LShift Ltd., Cohesive Financial Technologies LLC., and Rabbit Technologies Ltd.
        Licensed under the MPL.  See http://www.rabbitmq.com/

        node           : rabbit@ubuntu
        app descriptor : /usr/lib/rabbitmq/lib/rabbitmq_server-1.8.0/sbin/../ebin/rabbit.app
        home dir       : /var/lib/rabbitmq
        cookie hash    : mfoMkOc9CYok/SmH7RH9Jg==
        log            : /var/log/rabbitmq/rabbit@ubuntu.log
        sasl log       : /var/log/rabbitmq/rabbit@ubuntu-sasl.log
        database dir   : /var/lib/rabbitmq/mnesia/rabbit@ubuntu
        erlang version : 5.7.4

        starting file handle cache server                                     ...done
        starting worker pool                                                  ...done
        starting database                                                     ...done
        starting empty DB check                                               ...done
        starting exchange recovery                                            ...done
        starting queue supervisor and queue recovery                          ...BOOT ERROR: FAILED


    Note:
        Please refer to its super-class ``LogFileOutput``
    """
    pass


@mapper("rabbitmq_startup_err")
class RabbitMQStartupErrLog(LogFileOutput):
    """Class for parsing ``/var/log/rabbitmq/startup_err`` file.

    Typical content of ``startup_err`` file is::

        Error: {node_start_failed,normal}

        Crash dump was written to: erl_crash.dump
        Kernel pid terminated (application_controller) ({application_start_failure,kernel,{shutdown,{kernel,start,[normal,[]]}}})

    Note:
        Please refer to its super-class ``LogFileOutput``
    """
    pass
