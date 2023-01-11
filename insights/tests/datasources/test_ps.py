import json
import pytest
import shutil
import tempfile

from mock.mock import Mock

from insights.core.exceptions import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.specs.datasources.ps import ps_eo_cmd, LocalSpecs, jboss_runtime_versions

PS_DATA = """
PID COMMAND
  1 /usr/lib/systemd/systemd --switched-root --system --deserialize 31
  2 [kthreadd]
  3 [rcu_gp]
  4 [rcu_par_gp]
  6 [kworker/0:0H-events_highpri]
  9 [mm_percpu_wq]
 10 [rcu_tasks_kthre]
 11 /usr/bin/python3 /home/user1/python_app.py
 12 [kworker/u16:0-kcryptd/253:0]
"""

PS_EXPECTED = """
PID COMMAND
1 /usr/lib/systemd/systemd
2 [kthreadd]
3 [rcu_gp]
4 [rcu_par_gp]
6 [kworker/0:0H-events_highpri]
9 [mm_percpu_wq]
10 [rcu_tasks_kthre]
11 /usr/bin/python3
12 [kworker/u16:0-kcryptd/253:0]
"""

PS_BAD = "Command not found"

PS_EMPTY = """
PID COMMAND
"""
jboss_home_1 = tempfile.mkdtemp(prefix='insights_test')
jboss_home_2 = tempfile.mkdtemp(prefix='insights_test')
PS_JBOSS_VERSION = """
    PID COMMAND
    1 /usr/lib/systemd/systemd --switched-root --system --deserialize 17
    2 [kthreadd]
    3 [rcu_gp]
    8686 java -D[Standalone] -server -verbose:gc -Xloggc:/opt/jboss-datagrid-7.3.0-server/standalone/log/gc.log -XX:+PrintGCDetails -XX:+UseGCLogFileRotation -XX:NumberOfGCLogFiles=5 -XX:GCLogFileSize=3M -XX:-TraceClassUnloading -Xms64m -Xmx512m -XX:MetaspaceSize=96M -XX:MaxMetaspaceSize=256m -Djava.net.preferIPv4Stack=true -Djboss.modules.system.pkgs=org.jboss.byteman -Djava.awt.headless=true -Dorg.jboss.boot.log.file=/opt/jboss-datagrid-7.3.0-server/standalone/log/server.log -Dlogging.configuration=file:/opt/jboss-datagrid-7.3.0-server/standalone/configuration/logging.properties -jar /opt/jboss-datagrid-7.3.0-server/jboss-modules.jar -mp /opt/jboss-datagrid-7.3.0-server/modules org.jboss.as.standalone -Djboss.home.dir={0} -Djboss.server.base.dir=/opt/jboss-datagrid-7.3.0-server/standalone
    8880 /usr/lib/jvm/java-1.8.0-oracle/bin/java -D[Process Controller] -server -Xms64m -Xmx512m -XX:MaxMetaspaceSize=256m -Djava.net.preferIPv4Stack=true -Djboss.modules.system.pkgs=org.jboss.byteman -Djava.awt.headless=true -Dorg.jboss.boot.log.file=/home/jboss/jboss-eap-7.1/domain/log/process-controller.log -Dlogging.configuration=file:/home/jboss/jboss-eap-7.1/domain/configuration/logging.properties -jar /home/jboss/jboss-eap-7.1/jboss-modules.jar -mp /home/jboss/jboss-eap-7.1/modules org.jboss.as.process-controller -jboss-home {1} -jvm /usr/lib/jvm/java-1.8.0-oracle/bin/java -mp /home/jboss/jboss-eap-7.1/modules -- -Dorg.jboss.boot.log.file=/home/jboss/jboss-eap-7.1/domain/log/host-controller.log -Dlogging.configuration=file:/home/jboss/jboss-eap-7.1/domain/configuration/logging.properties -server
""".format(jboss_home_1, jboss_home_2)

RELATIVE_PATH = 'insights_commands/ps_eo_cmd'
JBOSS_VERSION_PATH = 'insights_commands/jboss_versions'


def test_ps_eo_cmd():
    ps_eo_args = Mock()
    ps_eo_args.content = PS_DATA.splitlines()
    broker = {LocalSpecs.ps_eo_args: ps_eo_args}
    result = ps_eo_cmd(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    expected = DatasourceProvider(content=PS_EXPECTED.strip(), relative_path=RELATIVE_PATH)
    assert result.content == expected.content
    assert result.relative_path == expected.relative_path


def test_ps_eo_cmd_bad():
    ps_eo_args = Mock()
    ps_eo_args.content = PS_BAD.splitlines()
    broker = {LocalSpecs.ps_eo_args: ps_eo_args}
    with pytest.raises(SkipComponent) as e:
        ps_eo_cmd(broker)
    assert e is not None


def test_ps_eo_cmd_empty():
    ps_eo_args = Mock()
    ps_eo_args.content = PS_EMPTY.splitlines()
    broker = {LocalSpecs.ps_eo_args: ps_eo_args}
    with pytest.raises(SkipComponent) as e:
        ps_eo_cmd(broker)
    assert e is not None


def test_jboss_versions():
    # create version.txt file
    with open(jboss_home_1 + '/version.txt', 'w') as j_v:
        j_v.write("Red Hat JBoss Enterprise Application Platform - Version 7.4.0.GA")
    with open(jboss_home_2 + '/version.txt', 'w') as j_v:
        j_v.write("Red Hat Data Grid - Version 8.3.1.GA")
    ps_eo_args = Mock()
    ps_eo_args.content = PS_JBOSS_VERSION.splitlines()
    broker = {LocalSpecs.ps_eo_args: ps_eo_args}
    result = jboss_runtime_versions(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    expected_content = {jboss_home_1: 'Red Hat JBoss Enterprise Application Platform - Version 7.4.0.GA',
                        jboss_home_2: 'Red Hat Data Grid - Version 8.3.1.GA'}
    expected = DatasourceProvider(content=json.dumps(expected_content), relative_path=JBOSS_VERSION_PATH)
    result_dict = json.loads(result.content[0])
    assert result_dict == expected_content
    assert result.relative_path == expected.relative_path
    shutil.rmtree(jboss_home_1)
    shutil.rmtree(jboss_home_2)
