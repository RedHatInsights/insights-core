import pytest
from mock.mock import Mock

from insights.core.dr import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.specs.datasources.ps import ps_eo_cmd, LocalSpecs

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

RELATIVE_PATH = 'insights_commands/ps_eo_cmd'


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
