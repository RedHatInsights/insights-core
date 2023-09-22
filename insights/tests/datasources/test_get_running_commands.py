import pytest

from insights.combiners.ps import Ps
from insights.parsers.ps import PsEoCmd
from insights.specs.datasources import get_running_commands
from insights.tests import context_wrap

PS_EO_CMD = """
   PID COMMAND
     1 /usr/lib/systemd/systemd --switched-root --system --deserialize 22
     2 [kthreadd]
   988 /usr/sbin/httpd -DFOREGROUND
  1036 /usr/sbin/httpd -DFOREGROUND
  1037 /usr/sbin/httpd -DFOREGROUND
  1038 /usr/sbin/httpd -DFOREGROUND
  1039 /usr/sbin/httpd -DFOREGROUND
  1040 /usr/local/sbin/httpd -DFOREGROUND
 28218 /usr/bin/java TestSleepMethod1
 28219 java TestSleepMethod1
 28240 /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.292.b10-1.el7_9.x86_64/jre/bin/java TestSleepMethod2
333083 /home/user3/apps/pycharm-2021.1.1/jbr/bin/java -classpath /home/user3/apps/pycharm-2021.1.1/lib/bootstrap.jar:/home/user3/apps/pycharm-2021.1.1/lib/util.jar:/home/user3/apps/pycharm-2021.1.1/lib/jdom.jar:/home/user3/apps/pycharm-2021.1.1/lib/log4j.jar:/home/user3/apps/pycharm-2021.1.1/lib/jna.jar -Xms128m -Xmx2048m -XX:ReservedCodeCacheSize=512m -XX:+UseG1GC -XX:SoftRefLRUPolicyMSPerMB=50 -XX:CICompilerCount=2 -XX:+HeapDumpOnOutOfMemoryError -XX:-OmitStackTraceInFastThrow -ea -Dsun.io.useCanonCaches=false -Djdk.http.auth.tunneling.disabledSchemes="" -Djdk.attach.allowAttachSelf=true -Djdk.module.illegalAccess.silent=true -Dkotlinx.coroutines.debug=off -Dsun.tools.attach.tmp.only=true -XX:ErrorFile=/home/user3/java_error_in_pycharm_%p.log -XX:HeapDumpPath=/home/user3/java_error_in_pycharm_.hprof -Didea.vendor.name=JetBrains -Didea.paths.selector=PyCharm2021.1 -Djb.vmOptionsFile=/home/user3/.config/JetBrains/PyCharm2021.1/pycharm64.vmoptions -Didea.platform.prefix=Python com.intellij.idea.Main
"""

PS_EO_CMD_MISSING = """
PID COMMAND
  1 /usr/lib/systemd/systemd --switched-root --system --deserialize 22
  2 [kthreadd]
"""

PS_EO_CMD_EXCEPTION = """
  PID COMMAND
    1 /usr/lib/systemd/systemd --switched-root --system --deserialize 22
    2 [kthreadd]
28218 /usr/bin/java TestSleepMethod1
28219 /exception/java
"""

PS_EO_CMD_ONE = """
   PID COMMAND
     1 /usr/lib/systemd/systemd --switched-root --system --deserialize 22
     2 [kthreadd]
   988 /usr/sbin/httpd -DFOREGROUND
"""


class FakeContext(object):
    def shell_out(self, cmd, split=True, timeout=None, keep_rc=False, env=None, signum=None):
        tmp_cmd = cmd.strip().split()
        if 'exception' in tmp_cmd[-1]:
            raise Exception()
        elif tmp_cmd[-1].startswith('/'):
            return [tmp_cmd[-1], ]
        elif tmp_cmd[-1].endswith('java'):
            return ['/usr/bin/java', ]
        elif tmp_cmd[-1].endswith('httpd'):
            return ['/usr/sbin/httpd', ]

        raise Exception()


def test_get_running_commands_present():
    pseo = PsEoCmd(context_wrap(PS_EO_CMD))
    ps = Ps(None, None, None, None, None, None, pseo)
    assert ps is not None
    ctx = FakeContext()

    results = get_running_commands(ps, ctx, ['httpd'])
    assert set(results) == set(['/usr/sbin/httpd', '/usr/local/sbin/httpd'])

    results = get_running_commands(ps, ctx, ['java'])
    assert set(results) == set([
        '/usr/bin/java',
        '/home/user3/apps/pycharm-2021.1.1/jbr/bin/java',
        '/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.292.b10-1.el7_9.x86_64/jre/bin/java'
    ])

    results = get_running_commands(ps, ctx, ['java', 'httpd'])
    assert set(results) == set([
        '/usr/bin/java',
        '/home/user3/apps/pycharm-2021.1.1/jbr/bin/java',
        '/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.292.b10-1.el7_9.x86_64/jre/bin/java',
        '/usr/sbin/httpd',
        '/usr/local/sbin/httpd'
    ])


def test_get_running_commands_missing():
    pseo = PsEoCmd(context_wrap(PS_EO_CMD_MISSING))
    ps = Ps(None, None, None, None, None, None, pseo)
    assert ps is not None
    ctx = FakeContext()

    results = get_running_commands(ps, ctx, ['httpd', 'java'])
    assert set(results) == set()


def test_get_running_commands_cmd_exception():
    pseo = PsEoCmd(context_wrap(PS_EO_CMD_EXCEPTION))
    ps = Ps(None, pseo, None, None, None, None, pseo)
    assert ps is not None
    ctx = FakeContext()

    results = get_running_commands(ps, ctx, ['httpd', 'java'])
    assert set(results) == set(['/usr/bin/java', ])


def test_get_running_commands_exception():
    pseo = PsEoCmd(context_wrap(PS_EO_CMD_MISSING))
    ps = Ps(None, None, None, None, None, None, pseo)
    assert ps is not None
    ctx = FakeContext()

    with pytest.raises(TypeError):
        get_running_commands(ps, ctx, 'not_a_list')

    with pytest.raises(TypeError):
        get_running_commands(ps, ctx, [])


def test_get_running_commands_one():
    pseo = PsEoCmd(context_wrap(PS_EO_CMD_ONE))
    ps = Ps(None, None, None, None, None, None, pseo)
    assert ps is not None
    ctx = FakeContext()

    results = get_running_commands(ps, ctx, ['httpd'])
    assert set(results) == set(['/usr/sbin/httpd', ])
