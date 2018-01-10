"""
RabbitMQ Logs
=============

Module for parsing the log files for RabbitMQ:

RabbitMQLogs - file ``/var/log/rabbitmq/rabbit@$HOSTNAME.log``
--------------------------------------------------------------

RabbitMQStartupErrLog - file ``/var/log/rabbitmq/startup_err``
--------------------------------------------------------------

RabbitMQStartupLog - file ``/var/log/rabbitmq/startup_log``
-----------------------------------------------------------

"""

from .. import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.rabbitmq_startup_log)
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


@parser(Specs.rabbitmq_startup_err)
class RabbitMQStartupErrLog(LogFileOutput):
    """Class for parsing ``/var/log/rabbitmq/startup_err`` file.

    Typical content of ``startup_err`` file is::

        Error: {node_start_failed,normal}

        Crash dump was written to: erl_crash.dump
        Kernel pid terminated (application_controller) ({application_start_failure,kernel,{shutdown,{kernel,start,[normal,[]]}}})

    .. note::
        Please refer to its super-class :py:class:`insights.core.LogFileOutput`
    """
    pass


@parser(Specs.rabbitmq_logs)
class RabbitMQLogs(LogFileOutput):
    """Class for parsing ``/var/log/rabbitmq/rabbit@$HOSTNAME.log`` file

    Typical content of ``rabbit@$HOSTNAME.log`` file is::

        =INFO REPORT==== 9-Nov-2016::14:29:11 ===
        Starting RabbitMQ 3.6.3 on Erlang 18.3.4.4
        Copyright (C) 2007-2016 Pivotal Software, Inc.
        Licensed under the MPL.  See http://www.rabbitmq.com/

        =INFO REPORT==== 9-Nov-2016::14:29:11 ===
        node           : rabbit@overcloud-controller-0
        home dir       : /var/lib/rabbitmq
        config file(s) : /etc/rabbitmq/rabbitmq.config
        cookie hash    : F7g8XhNTzvEK3KywLHh9yA==
        log            : /var/log/rabbitmq/rabbit@overcloud-controller-0.log
        sasl log       : /var/log/rabbitmq/rabbit@overcloud-controller-0-sasl.log
        database dir   : /var/lib/rabbitmq/mnesia/rabbit@overcloud-controller-0
        ...

    .. note::
        Please refer to its super-class :py:class:`insights.core.LogFileOutput`
        for full usage.

    .. note::
        Because this parser is defined using a PatternSpec, which returns
        multiple files, the data in the shared parser state is a list of
        these parser objects.  This means that for the moment you will have
        to iterate across these objects directly.

    Examples:
        >>> for log in shared[RabbitMQLogs]:
        ...     print 'log file:', log.file_path
        ...     print 'INFO lines:', len(log.get('INFO REPORT'))
        ...     print 'ERROR lines:', len(log.get('ERROR REPORT'))
        ...
        log file: /var/log/rabbitmq/rabbit@queue.example.com.log
        INFO lines: 2
        ERROR lines: 0
    """
    time_format = '%d-%b-%Y::%H:%M:%S'
