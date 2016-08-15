from falafel.mappers.corosync import CoroSyncConfig
from falafel.tests import context_wrap

corosync_content = """
# Corosync init script configuration file

# COROSYNC_INIT_TIMEOUT specifies number of seconds to wait for corosync
# initialization (default is one minute).
COROSYNC_INIT_TIMEOUT = 60

# COROSYNC_OPTIONS specifies options passed to corosync command
# (default is no options).
# See "man corosync" for detailed descriptions of the options.
COROSYNC_OPTIONS=""
"""


def test_corosync_1():
    result = CoroSyncConfig.parse_context(context_wrap(corosync_content))
    assert result.data['COROSYNC_OPTIONS'] == ""
    assert result.data['COROSYNC_INIT_TIMEOUT'] == "60"
