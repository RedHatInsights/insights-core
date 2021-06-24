import pytest

from insights.combiners.ps import Ps
from insights.parsers.ps import PsAuxww
from insights.specs.datasources import get_running_commands
from insights.tests import context_wrap

PS_AUXWW = """
USER       PID %CPU %MEM     VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.1  193720  6908 ?        Ss   Jun22   0:40 /usr/lib/systemd/systemd --switched-root --system --deserialize 22
root         2  0.0  0.0       0     0 ?        S    Jun22   0:00 [kthreadd]
root       988  0.0  0.1  228304  5144 ?        Ss   Jun22   0:11 /usr/sbin/httpd -DFOREGROUND
apache    1036  0.0  0.0  228304  2972 ?        S    Jun22   0:00 /usr/sbin/httpd -DFOREGROUND
apache    1037  0.0  0.0  228304  2972 ?        S    Jun22   0:00 /usr/sbin/httpd -DFOREGROUND
apache    1038  0.0  0.0  228304  2972 ?        S    Jun22   0:00 /usr/sbin/httpd -DFOREGROUND
apache    1039  0.0  0.0  228304  2972 ?        S    Jun22   0:00 /usr/sbin/httpd -DFOREGROUND
apache    1040  0.0  0.0  228304  2972 ?        S    Jun22   0:00 /usr/local/sbin/httpd -DFOREGROUND
user1    28218  0.9  0.5 3017456  23924 pts/0   Sl   18:13   0:00 /usr/bin/java TestSleepMethod1
user1    28219  0.9  0.5 3017456  23924 pts/0   Sl   18:13   0:00 java TestSleepMethod1
user2    28240  1.6  0.5 3017456  23856 pts/0   Sl   18:13   0:00 /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.292.b10-1.el7_9.x86_64/jre/bin/java TestSleepMethod2
user3   333083 12.4  8.5 10780332 2748620 ?     Sl   09:46  62:47 /home/user3/apps/pycharm-2021.1.1/jbr/bin/java -classpath /home/user3/apps/pycharm-2021.1.1/lib/bootstrap.jar:/home/user3/apps/pycharm-2021.1.1/lib/util.jar:/home/user3/apps/pycharm-2021.1.1/lib/jdom.jar:/home/user3/apps/pycharm-2021.1.1/lib/log4j.jar:/home/user3/apps/pycharm-2021.1.1/lib/jna.jar -Xms128m -Xmx2048m -XX:ReservedCodeCacheSize=512m -XX:+UseG1GC -XX:SoftRefLRUPolicyMSPerMB=50 -XX:CICompilerCount=2 -XX:+HeapDumpOnOutOfMemoryError -XX:-OmitStackTraceInFastThrow -ea -Dsun.io.useCanonCaches=false -Djdk.http.auth.tunneling.disabledSchemes="" -Djdk.attach.allowAttachSelf=true -Djdk.module.illegalAccess.silent=true -Dkotlinx.coroutines.debug=off -Dsun.tools.attach.tmp.only=true -XX:ErrorFile=/home/user3/java_error_in_pycharm_%p.log -XX:HeapDumpPath=/home/user3/java_error_in_pycharm_.hprof -Didea.vendor.name=JetBrains -Didea.paths.selector=PyCharm2021.1 -Djb.vmOptionsFile=/home/user3/.config/JetBrains/PyCharm2021.1/pycharm64.vmoptions -Didea.platform.prefix=Python com.intellij.idea.Main
"""

PS_AUXWW_MISSING = """
USER       PID %CPU %MEM     VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.1  193720  6908 ?        Ss   Jun22   0:40 /usr/lib/systemd/systemd --switched-root --system --deserialize 22
root         2  0.0  0.0       0     0 ?        S    Jun22   0:00 [kthreadd]
"""

PS_AUXWW_EXCEPTION = """
USER       PID %CPU %MEM     VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.1  193720  6908 ?        Ss   Jun22   0:40 /usr/lib/systemd/systemd --switched-root --system --deserialize 22
root         2  0.0  0.0       0     0 ?        S    Jun22   0:00 [kthreadd]
user1    28218  0.9  0.5 3017456  23924 pts/0   Sl   18:13   0:00 /usr/bin/java TestSleepMethod1
user1    28219  0.9  0.5 3017456  23924 pts/0   Sl   18:13   0:00 /exception/java
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
    psauxww = PsAuxww(context_wrap(PS_AUXWW))
    ps = Ps(None, psauxww, None, None, None, None)
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
    psauxww = PsAuxww(context_wrap(PS_AUXWW_MISSING))
    ps = Ps(None, psauxww, None, None, None, None)
    assert ps is not None
    ctx = FakeContext()

    results = get_running_commands(ps, ctx, ['httpd', 'java'])
    assert set(results) == set()


def test_get_running_commands_cmd_exception():
    psauxww = PsAuxww(context_wrap(PS_AUXWW_EXCEPTION))
    ps = Ps(None, psauxww, None, None, None, None)
    assert ps is not None
    ctx = FakeContext()

    results = get_running_commands(ps, ctx, ['httpd', 'java'])
    assert set(results) == set(['/usr/bin/java', ])


def test_get_running_commands_exception():
    psauxww = PsAuxww(context_wrap(PS_AUXWW_MISSING))
    ps = Ps(None, psauxww, None, None, None, None)
    assert ps is not None
    ctx = FakeContext()

    with pytest.raises(TypeError):
        get_running_commands(ps, ctx, 'not_a_list')

    with pytest.raises(TypeError):
        get_running_commands(ps, ctx, [])
