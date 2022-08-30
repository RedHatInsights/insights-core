import pytest
from mock.mock import patch
from insights.core.dr import SkipComponent
from insights.core.context import HostContext
from insights.specs.datasources.httpd import httpd_cmds, httpd_on_nfs
from insights.combiners.ps import Ps
from insights.combiners.mounts import Mounts
from insights.parsers.mount import Mount
from insights.tests import context_wrap


MOUNT_DATA = """
tmpfs on /tmp type tmpfs (rw,seclabel)
/dev/httpd on /httpd1 type nfs4 (rw,relatime,vers=4)
/dev/mapper/httpd on /httpd2 type nfs4 (rw,relatime,vers=4)
/dev/mapper/home on /home type ext4 (rw,relatime,seclabel,data=ordered)
/dev/mapper/root on / type ext4 (rw,relatime,seclabel,data=ordered)
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
    broker = {Mounts: Mounts(Mount(context_wrap(MOUNT_DATA)), None, None), HostContext: FakeContext()}
    result = httpd_on_nfs(broker)
    assert result.content == ['{"http_ids": ["666", "777"], "nfs_mounts": ["/httpd1", "/httpd2"], "open_nfs_files": 5}']
