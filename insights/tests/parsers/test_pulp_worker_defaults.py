from insights.parsers import pulp_worker_defaults
from insights.tests import context_wrap

import doctest

pulp_worker_defaults_in_docs = '''
# Configuration file for Pulp's Celery workers

# Define the number of worker nodes you wish to have here. This defaults to the number of processors
# that are detected on the system if left commented here.
PULP_CONCURRENCY=1

# Configure Python's encoding for writing all logs, stdout and stderr
PYTHONIOENCODING="UTF-8"
'''


def test_pulp_worker_defaults_docs():
    env = {
        'PulpWorkerDefaults': pulp_worker_defaults.PulpWorkerDefaults,
        'shared': {
            pulp_worker_defaults.PulpWorkerDefaults: pulp_worker_defaults.PulpWorkerDefaults(
                context_wrap(pulp_worker_defaults_in_docs)
            )
        },
    }
    failed, total = doctest.testmod(pulp_worker_defaults, globs=env)
    assert failed == 0
