from insights.parsers.rabbitmq_log import RabbitMQStartupLog
from insights.parsers.rabbitmq_log import RabbitMQStartupErrLog
from insights.parsers.rabbitmq_log import RabbitMQLogs
from insights.tests import context_wrap

from datetime import datetime

STARTUP_LOG = """
starting file handle cache server                                     ...done
starting worker pool                                                  ...done
starting database                                                     ...done
starting empty DB check                                               ...done
starting exchange recovery                                            ...done
starting queue supervisor and queue recovery                          ...BOOT ERROR: FAILED
"""

STARTUP_ERR_LOG = """
Error: {node_start_failed,normal}

Crash dump was written to: erl_crash.dump
Kernel pid terminated (application_controller) ({application_start_failure,kernel,{shutdown,{kernel,start,[normal,[]]}}})
"""


def test_rabbitmq_startup_log():
    log = RabbitMQStartupLog(context_wrap(STARTUP_LOG))
    assert len(log.get('done')) == 5


def test_rabbitmq_start_err_log():
    log = RabbitMQStartupErrLog(context_wrap(STARTUP_ERR_LOG))
    assert len(log.get('Error')) == 1


RABBIT_MQ_LOG = """
=INFO REPORT==== 7-Jun-2015::03:42:13 ===
accepting AMQP connection <0.13548.17> (192.168.100.40:59815 -> 192.168.100.41:5672)

=ERROR REPORT==== 7-Jun-2015::03:42:28 ===
AMQP connection <0.13548.17> (running), channel 19793 - error:
{amqp_error,frame_error,
            "type 65, all octets = <<>>: {frame_too_large,1342177289,131064}",
            none}

=ERROR REPORT==== 7-Jun-2015::03:42:31 ===
closing AMQP connection <0.13548.17> (192.168.100.40:59815 -> 192.168.100.41:5672):
fatal_frame_error
""".strip()


def test_rabbitmq_log():
    # Note that this tests one file - normally shared[RabbitMQLogs] will
    # contain multiple parser objects.
    log = RabbitMQLogs(context_wrap(RABBIT_MQ_LOG, path='/var/log/rabbitmq/rabbit@queue.example.com.log'))
    assert len(log.get('AMQP')) == 3
    assert len(list(log.get_after(datetime(2015, 6, 7, 3, 42, 20)))) == 9
