import pytest
from mock.mock import patch
from insights.core.dr import SkipComponent
from insights.core.context import HostContext
from insights.specs.datasources.httpd import httpd_cmds
from insights.combiners.ps import Ps


# The ``get_running_commands()`` is tested in:
# - insights/tests/datasources/test_get_running_commands.py
# Here, we do not test it
@patch('insights.specs.datasources.httpd.get_running_commands')
def test_httpd_cmds(run_cmds):
    broker = {Ps: None, HostContext: None}
    httpds = ['/usr/sbin/httpd/', '/opt/rh/httpd24/root/usr/sbin/httpd']
    run_cmds.return_value = httpds
    result = httpd_cmds(broker)
    assert result == httpds

    run_cmds.return_value = []
    with pytest.raises(SkipComponent):
        httpd_cmds(broker)
