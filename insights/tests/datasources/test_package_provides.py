import pytest

from insights import dr, HostContext
from insights.combiners.ps import Ps
from insights.core import filters
from insights.core.dr import SkipComponent
from insights.parsers.ps import PsEoCmd
from insights.specs import Specs
from insights.specs.datasources.package_provides import get_package, cmd_and_pkg
from insights.core.spec_factory import DatasourceProvider
from insights.tests import context_wrap

JAVA_PATH_1 = '/usr/bin/java'
JAVA_PATH_2 = '/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.292.b10-1.el7_9.x86_64/jre/bin/java'
JAVA_PATH_BAD = '/random/java'
JAVA_PATH_ERR = '/error/java'
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
            elif arg == JAVA_PATH_ERR:
                return (1, ['file not found', ])
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


def setup_function(func):
    if Specs.package_provides_command in filters._CACHE:
        del filters._CACHE[Specs.package_provides_command]
    if Specs.package_provides_command in filters.FILTERS:
        del filters.FILTERS[Specs.package_provides_command]

    if func is test_cmd_and_pkg:
        filters.add_filter(Specs.package_provides_command, ['httpd', 'java'])
    elif func is test_cmd_and_pkg_not_found:
        filters.add_filter(Specs.package_provides_command, ['not_found'])


def teardown_function(func):
    if func is test_cmd_and_pkg or func is test_cmd_and_pkg_not_found:
        del filters.FILTERS[Specs.package_provides_command]


def test_get_package():
    ctx = FakeContext()

    result = get_package(ctx, '/usr/bin/java')
    print('result:', result)
    assert result == 'java-1.8.0-openjdk-headless-1.8.0.292.b10-1.el7_9.x86_64'

    result = get_package(ctx, '/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.292.b10-1.el7_9.x86_64/jre/bin/java')
    assert result == 'java-1.8.0-openjdk-headless-1.8.0.292.b10-1.el7_9.x86_64'


def test_get_package_bad():
    ctx = FakeContext()

    result = get_package(ctx, JAVA_PATH_BAD)
    assert result is None


def test_get_package_err():
    ctx = FakeContext()

    result = get_package(ctx, JAVA_PATH_ERR)
    assert result is None


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

EXPECTED = DatasourceProvider(
    "\n".join([
        "{0} {1}".format(HTTPD_PATH, HTTPD_PKG),
        "{0} {1}".format(JAVA_PATH_1, JAVA_PKG_2),
        "{0} {1}".format(JAVA_PATH_2, JAVA_PKG_2)
    ]),
    relative_path='insights_commands/package_provides_command'
)


def test_cmd_and_pkg():
    pseo = PsEoCmd(context_wrap(PS_EO_CMD))
    ps = Ps(None, None, None, None, None, None, pseo)
    broker = dr.Broker()
    broker[HostContext] = FakeContext()
    broker[Ps] = ps

    result = cmd_and_pkg(broker)
    assert result is not None
    assert sorted(result.content) == sorted(EXPECTED.content)


def test_cmd_and_pkg_no_filters():
    pseo = PsEoCmd(context_wrap(PS_EO_CMD))
    ps = Ps(None, None, None, None, None, None, pseo)
    broker = dr.Broker()
    broker[HostContext] = FakeContext()
    broker[Ps] = ps

    with pytest.raises(SkipComponent):
        cmd_and_pkg(broker)


def test_cmd_and_pkg_not_found():
    pseo = PsEoCmd(context_wrap(PS_EO_CMD))
    ps = Ps(None, None, None, None, None, None, pseo)
    broker = dr.Broker()
    broker[HostContext] = FakeContext()
    broker[Ps] = ps

    with pytest.raises(SkipComponent):
        cmd_and_pkg(broker)
