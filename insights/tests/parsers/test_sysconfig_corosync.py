from insights.parsers.sysconfig import CorosyncSysconfig
from insights.tests import context_wrap

corosync_content = """
# Corosync init script configuration file

# COROSYNC_INIT_TIMEOUT specifies number of seconds to wait for corosync
# initialization (default is one minute).
COROSYNC_INIT_TIMEOUT=60

# COROSYNC_OPTIONS specifies options passed to corosync command
# (default is no options).
# See "man corosync" for detailed descriptions of the options.
COROSYNC_OPTIONS=""
"""


def test_corosync_sysconfig():
    result = CorosyncSysconfig(context_wrap(corosync_content))
    assert result.data['COROSYNC_OPTIONS'] == ""
    assert result.data['COROSYNC_INIT_TIMEOUT'] == "60"

    assert result.options == ''
    assert result.unparsed_lines == []
