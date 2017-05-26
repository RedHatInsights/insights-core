from insights.mappers.rabbitmq_log import RabbitMQStartupLog
from insights.mappers.rabbitmq_log import RabbitMQStartupErrLog
from insights.tests import context_wrap


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
