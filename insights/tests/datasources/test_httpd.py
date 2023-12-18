import pytest

from mock.mock import mock_open
from insights.combiners.ps import Ps
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.parsers.mount import ProcMounts
from insights.specs.datasources.httpd import httpd_cmds, httpd_on_nfs, httpd_configuration_files, httpd24_scl_configuration_files, httpd24_scl_jbcs_configuration_files
from insights.tests import context_wrap


try:
    from unittest.mock import patch
    builtin_open = "builtins.open"
except Exception:
    from mock import patch
    builtin_open = "__builtin__.open"


MOUNT_DATA = """
/dev/mapper/root / ext4 rw,relatime,barrier=1,data=ordered 0 0
/dev/mapper/httpd1 /httpd1 nfs4 rw,relatime,vers=4,barrier=1,data=ordered 0 0
/dev/mapper/httpd2 /httpd2 nfs4 rw,relatime,vers=4,barrier=1,data=ordered 0 0
""".strip()
NFS_LSOF_666 = """
zsh     3520 httpd    3r   REG  253,0   6940392    648646 /httpd1
zsh     3520 httpd   11r   REG  253,0   9253600    648644 /httpd1
zsh     3520 httpd   12u   CHR    5,0       0t0      1034 /dev/tty
""".strip()
NFS_LSOF_777 = """
zsh     3520 httpd    3r   REG  253,0   6940392    648646 /httpd2
zsh     3520 httpd   11r   REG  253,0   9253600    648644 /httpd2
zsh     3520 httpd   12u   CHR    5,0       0t0      1034 /httpd2
""".strip()


class FakeContext(HostContext):
    def shell_out(self, cmd, split=True, timeout=None, keep_rc=False, env=None, signum=None):
        if 'pgrep' in cmd:
            return '666', '777'
        elif 'lsof -p 666' in cmd:
            return NFS_LSOF_666.splitlines()
        elif 'lsof -p 777' in cmd:
            return NFS_LSOF_777.splitlines()

        raise Exception


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


@patch('insights.specs.datasources.httpd.get_running_commands')
def test_httpd_on_nfs(run_cmds):
    broker = {ProcMounts: ProcMounts(context_wrap(MOUNT_DATA)), HostContext: FakeContext()}
    result = httpd_on_nfs(broker)
    assert '"http_ids": ["666", "777"]' in result.content[0]
    assert '"open_nfs_files": 5' in result.content[0]
    assert '"nfs_mounts": ["/httpd1", "/httpd2"]' in result.content[0]


data_lines_httpd_conf = """
ServerRoot "/etc/httpd"
Include conf.d/*.conf
""".strip()

data_lines_httpd24_scl_conf = """
ServerRoot "/opt/rh/httpd24/root/etc/httpd"
Include conf.d/*.conf
""".strip()

data_lines_httpd24_scl_jbcs_conf = """
ServerRoot "/opt/rh/jbcs-httpd24/root/etc/httpd"
Include conf.d/*.conf
""".strip()

data_lines_ssl_conf = """
Listen 443 https
""".strip()


@patch("os.path.isfile", return_value=True)
@patch("os.path.isdir", return_value=True)
@patch("glob.glob", return_value=["/etc/httpd/conf.d/ssl.conf"])
@patch(builtin_open, new_callable=mock_open, read_data=data_lines_httpd_conf)
def test_httpd_conf_files(m_open, m_glob, m_isdir, m_isfile):
    handlers = (m_open.return_value, mock_open(read_data=data_lines_ssl_conf).return_value)
    m_open.side_effect = handlers
    broker = {HostContext: None}
    result = httpd_configuration_files(broker)
    assert result == set(['/etc/httpd/conf.d/ssl.conf', '/etc/httpd/conf/httpd.conf'])


@patch("os.path.isfile", return_value=True)
@patch("os.path.isdir", return_value=True)
@patch("glob.glob", return_value=["/opt/rh/httpd24/root/etc/httpd/conf.d/ssl.conf"])
@patch(builtin_open, new_callable=mock_open, read_data=data_lines_httpd24_scl_conf)
def test_httpd24_scl_conf_files(m_open, m_glob, m_isdir, m_isfile):
    handlers = (m_open.return_value, mock_open(read_data=data_lines_ssl_conf).return_value)
    m_open.side_effect = handlers
    broker = {HostContext: None}
    result = httpd24_scl_configuration_files(broker)
    assert result == set(['/opt/rh/httpd24/root/etc/httpd/conf.d/ssl.conf', '/opt/rh/httpd24/root/etc/httpd/conf/httpd.conf'])


@patch("os.path.isfile", return_value=True)
@patch("os.path.isdir", return_value=True)
@patch("glob.glob", return_value=["/opt/rh/jbcs-httpd24/root/etc/httpd/conf.d/ssl.conf"])
@patch(builtin_open, new_callable=mock_open, read_data=data_lines_httpd24_scl_jbcs_conf)
def test_httpd24_scl_jbs_conf_files(m_open, m_glob, m_isdir, m_isfile):
    handlers = (m_open.return_value, mock_open(read_data=data_lines_ssl_conf).return_value)
    m_open.side_effect = handlers
    broker = {HostContext: None}
    result = httpd24_scl_jbcs_configuration_files(broker)
    assert result == set(['/opt/rh/jbcs-httpd24/root/etc/httpd/conf.d/ssl.conf', '/opt/rh/jbcs-httpd24/root/etc/httpd/conf/httpd.conf'])
