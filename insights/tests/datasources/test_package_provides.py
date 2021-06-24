from insights import dr, HostContext
from insights.combiners.ps import Ps
from insights.core import filters
from insights.parsers.ps import PsAuxww
from insights.specs import Specs
from insights.specs.datasources.package_provides import get_package, cmd_and_pkg
from insights.core.spec_factory import DatasourceProvider
from insights.tests import context_wrap

JAVA_PATH_1 = '/usr/bin/java'
JAVA_PATH_2 = '/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.292.b10-1.el7_9.x86_64/jre/bin/java'
JAVA_PATH_BAD = '/random/java'
JAVA_PKG_2 = 'java-1.8.0-openjdk-headless-1.8.0.292.b10-1.el7_9.x86_64'
HTTPD_PATH = '/usr/sbin/httpd'
HTTPD_PKG = 'httpd-2.4.6-97.el7_9.x86_64'


class FakeContext(HostContext):
    def shell_out(self, cmd, split=True, timeout=None, keep_rc=False, env=None, signum=None):
        tmp_cmd = cmd.strip().split()
        shell_cmd = tmp_cmd[0]
        arg = tmp_cmd[-1]
        if 'readlink' in shell_cmd:
            if arg == JAVA_PATH_1:
                return (0, [JAVA_PATH_2, ])
            elif arg.startswith('/'):
                return (0, [arg, ])
        elif 'rpm' in shell_cmd:
            if arg == JAVA_PATH_2:
                return (0, [JAVA_PKG_2, ])
            elif arg == HTTPD_PATH:
                return (0, [HTTPD_PKG, ])
            else:
                return (1, ['file {0} is not owned by any package'.format(arg), ])
        elif 'which' in shell_cmd:
            if 'exception' in arg:
                raise Exception()
            elif arg.startswith('/'):
                return [tmp_cmd[-1], ]
            elif arg.endswith('java'):
                return ['/usr/bin/java', ]
            elif arg.endswith('httpd'):
                return ['/usr/sbin/httpd', ]

        raise Exception()


def test_get_package():
    ctx = FakeContext()

    result = get_package(ctx, '/usr/bin/java')
    print('result:', result)
    assert result == 'java-1.8.0-openjdk-headless-1.8.0.292.b10-1.el7_9.x86_64'

    result = get_package(ctx, '/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.292.b10-1.el7_9.x86_64/jre/bin/java')
    assert result == 'java-1.8.0-openjdk-headless-1.8.0.292.b10-1.el7_9.x86_64'

    result = get_package(ctx, JAVA_PATH_BAD)
    assert result is None


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

EXPECTED = DatasourceProvider(
    "\n".join([
        "{0} {1}".format(HTTPD_PATH, HTTPD_PKG),
        "{0} {1}".format(JAVA_PATH_1, JAVA_PKG_2),
        "{0} {1}".format(JAVA_PATH_2, JAVA_PKG_2)
    ]),
    relative_path='insights_commands/package_provides_command'
)


def test_cmd_and_pkg():
    psauxww = PsAuxww(context_wrap(PS_AUXWW))
    ps = Ps(None, psauxww, None, None, None, None)
    filters.add_filter(Specs.package_provides_command, ['httpd', 'java'])
    broker = dr.Broker()
    broker[HostContext] = FakeContext()
    broker[Ps] = ps

    result = cmd_and_pkg(broker)
    assert result is not None
    assert sorted(result.content) == sorted(EXPECTED.content)
