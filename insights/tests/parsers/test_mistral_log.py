import doctest
from datetime import datetime

from insights.parsers import mistral_log
from insights.tests import context_wrap

EXECUTOR_LOG_CONTENT = """
2019-03-01 13:54:41.091 26749 DEBUG oslo_concurrency.lockutils [-] Acquired semaphore "singleton_lock" lock /usr/lib/python2.7/site-packages/oslo_concurrency/lockutils.py:212
2019-03-01 13:54:41.091 26749 DEBUG oslo_concurrency.lockutils [-] Releasing semaphore "singleton_lock" lock /usr/lib/python2.7/site-packages/oslo_concurrency/lockutils.py:228
2019-03-01 13:54:41.092 26749 DEBUG oslo_service.service [-] Full set of CONF: _wait_for_exit_or_signal /usr/lib/python2.7/site-packages/oslo_service/service.py:303
2019-03-01 13:54:41.092 26749 DEBUG oslo_service.service [-] ******************************************************************************** log_opt_values /usr/lib/python2.7/site-packages/oslo_config/cfg.py:28
2019-03-01 14:36:55.134 26749 ERROR mistral.executors.default_executor Traceback (most recent call last):
2019-03-01 14:36:55.134 26749 ERROR mistral.executors.default_executor   File "/usr/lib/python2.7/site-packages/mistral/executors/default_executor.py", line 114, in run_action
2019-03-01 14:36:55.134 26749 ERROR mistral.executors.default_executor     result = action.run(action_ctx)
2019-03-01 14:36:55.134 26749 ERROR mistral.executors.default_executor   File "/usr/lib/python2.7/site-packages/mistral/actions/openstack/base.py", line 130, in run
2019-03-01 14:36:55.134 26749 ERROR mistral.executors.default_executor     (self.__class__.__name__, self.client_method_name, str(e))
2019-03-01 14:36:55.134 26749 ERROR mistral.executors.default_executor ActionException: HeatAction.stacks.get failed: ERROR: The Stack (overcloud) could not be found.
2019-03-01 14:36:55.134 26749 ERROR mistral.executors.default_executor
2019-03-01 14:36:55.227 26749 INFO mistral.executors.executor_server [req-acd6d78c-9f9e-4d6c-9d6c-09717635ac29 89665ff87df144128ada2b8c59ec62f1 e4d0868a0715411fa1481f8ccfb61414 - default default] Received RPC request 'run_action'[action_ex_id=68693a02-8817-409e-a8d9-3572e7773da3, action_cls_str=mistral.actions.openstack.actions.IronicAction, action_cls_attrs={u'client_method_name': u'node.list'}, params={associated: True}, timeout=None]
""".strip()

SAMPLE_LOG_CONTENT = """
2019-03-01 13:54:41.091 26749 DEBUG oslo_concurrency.lockutils [-] Acquired semaphore "singleton_lock" lock /usr/lib/python2.7/site-packages/oslo_concurrency/lockutils.py:212
2019-03-01 13:54:41.091 26749 DEBUG oslo_concurrency.lockutils [-] Releasing semaphore "singleton_lock" lock /usr/lib/python2.7/site-packages/oslo_concurrency/lockutils.py:228
2019-03-01 13:54:41.092 26749 DEBUG oslo_service.service [-] Full set of CONF: _wait_for_exit_or_signal /usr/lib/python2.7/site-packages/oslo_service/service.py:303
2019-03-01 13:54:41.133 26749 DEBUG oslo_concurrency.lockutils [-] Lock "service_coordinator" released by "mistral.service.coordination.register_membership" :: held 0.000s inner /usr/lib/python2.7/site-packages/oslo_concurrency/lockutils.py:285
2019-03-01 13:56:05.329 26749 INFO mistral.executors.executor_server [req-a1d40531-b3b9-4fdf-802f-0371bf364551 89665ff87df144128ada2b8c59ec62f1 e4d0868a0715411fa1481f8ccfb61414 - default default] Received RPC request 'run_action'[action_ex_id=7c2c79ba-d7c4-4c4d-9e51-684bab00e6a9, action_cls_str=mistral.actions.std_actions.NoOpAction, action_cls_attrs={}, params={}, timeout=None]
2019-03-01 14:36:55.134 26749 ERROR mistral.executors.default_executor ActionException: HeatAction.stacks.get failed: ERROR: The Stack (overcloud) could not be found.
""".strip()


def test_mistral_executor_log():
    log = mistral_log.MistralExecutorLog(context_wrap(EXECUTOR_LOG_CONTENT))
    assert len(log.get('ERROR')) == 7
    assert log.get('oslo_concurrency.lockutils')[0]['raw_message'] == EXECUTOR_LOG_CONTENT.splitlines()[0]
    assert len(list(log.get_after(datetime(2019, 3, 1, 14, 30, 0)))) == 8


def test_documentation():
    failed_count, tests = doctest.testmod(
        mistral_log,
        globs={'executor_log': mistral_log.MistralExecutorLog(context_wrap(SAMPLE_LOG_CONTENT))}
    )
    assert failed_count == 0
