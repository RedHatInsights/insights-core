import doctest

from insights.parsers import foreman_tasks_config
from insights.parsers.foreman_tasks_config import ForemanTasksConfig
from insights.tests import context_wrap

FOREMAN_TASKS_CONFIG = """
FOREMAN_USER=foreman
BUNDLER_EXT_HOME=/usr/share/foreman
RAILS_ENV=production
FOREMAN_LOGGING=warn
FOREMAN_LOGGING_SQL=warn
FOREMAN_TASK_PARAMS="-p foreman"
FOREMAN_LOG_DIR=/var/log/foreman

RUBY_GC_MALLOC_LIMIT=4000100
RUBY_GC_MALLOC_LIMIT_MAX=16000100
RUBY_GC_MALLOC_LIMIT_GROWTH_FACTOR=1.1
RUBY_GC_OLDMALLOC_LIMIT=16000100
RUBY_GC_OLDMALLOC_LIMIT_MAX=16000100

#Set the number of executors you want to run
#EXECUTORS_COUNT=1

#Set memory limit for executor process, before it's restarted automatically
#EXECUTOR_MEMORY_LIMIT=2gb

#Set delay before first memory polling to let executor initialize (in sec)
#EXECUTOR_MEMORY_MONITOR_DELAY=7200 #default: 2 hours

#Set memory polling interval, process memory will be checked every N seconds.
#EXECUTOR_MEMORY_MONITOR_INTERVAL=60
"""


def test_foreman_tasks_config():
    foreman_tasks_config = ForemanTasksConfig(context_wrap(FOREMAN_TASKS_CONFIG)).data
    assert foreman_tasks_config["RAILS_ENV"] == 'production'
    assert foreman_tasks_config.get("FOREMAN_LOGGING") == 'warn'
    assert len(foreman_tasks_config) == 12


def test_foreman_tasks_config_doc_examples():
    env = {
        'foreman_tasks_config': ForemanTasksConfig(context_wrap(FOREMAN_TASKS_CONFIG)).data,
    }
    failed, total = doctest.testmod(foreman_tasks_config, globs=env)
    assert failed == 0
