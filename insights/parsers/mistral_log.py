"""
MistralExecutorLog - file ``/var/log/mistral/executor.log``
===========================================================
"""

from insights import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.mistral_executor_log)
class MistralExecutorLog(LogFileOutput):
    """Parse the ``/var/log/mistral/executor.log`` file.

    Provide access to mistral executor log using the LogFileOutput parser class.

    Typical content of ``executor.log`` file is::

        2019-03-01 13:54:41.091 26749 DEBUG oslo_concurrency.lockutils [-] Acquired semaphore "singleton_lock" lock /usr/lib/python2.7/site-packages/oslo_concurrency/lockutils.py:212
        2019-03-01 13:54:41.091 26749 DEBUG oslo_concurrency.lockutils [-] Releasing semaphore "singleton_lock" lock /usr/lib/python2.7/site-packages/oslo_concurrency/lockutils.py:228
        2019-03-01 13:54:41.092 26749 DEBUG oslo_service.service [-] Full set of CONF: _wait_for_exit_or_signal /usr/lib/python2.7/site-packages/oslo_service/service.py:303
        2019-03-01 13:54:41.133 26749 DEBUG oslo_concurrency.lockutils [-] Lock "service_coordinator" released by "mistral.service.coordination.register_membership" :: held 0.000s inner /usr/lib/python2.7/site-packages/oslo_concurrency/lockutils.py:285
        2019-03-01 13:56:05.329 26749 INFO mistral.executors.executor_server [req-a1d40531-b3b9-4fdf-802f-0371bf364551 89665ff87df144128ada2b8c59ec62f1 e4d0868a0715411fa1481f8ccfb61414 - default default] Received RPC request 'run_action'[action_ex_id=7c2c79ba-d7c4-4c4d-9e51-684bab00e6a9, action_cls_str=mistral.actions.std_actions.NoOpAction, action_cls_attrs={}, params={}, timeout=None]
        2019-03-01 14:36:55.134 26749 ERROR mistral.executors.default_executor ActionException: HeatAction.stacks.get failed: ERROR: The Stack (overcloud) could not be found.

    Examples:
        >>> type(executor_log)
        <class 'insights.parsers.mistral_log.MistralExecutorLog'>
        >>> executor_log.get('mistral.executors.default_executor')[0].get('raw_message')
        '2019-03-01 14:36:55.134 26749 ERROR mistral.executors.default_executor ActionException: HeatAction.stacks.get failed: ERROR: The Stack (overcloud) could not be found.'
        >>> from datetime import datetime
        >>> len(list(executor_log.get_after(datetime(2019, 3, 1, 13, 56, 0))))
        2

    """
    pass
