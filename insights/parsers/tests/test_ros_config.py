from insights.parsers.ros_config import RosConfig
from insights.tests import context_wrap


ROS_CONFIG_INPUT = """
log mandatory on default {
    mem.util.used
    mem.physmem
    kernel.all.cpu.user
    kernel.all.cpu.sys
    kernel.all.cpu.nice
    kernel.all.cpu.steal
    kernel.all.cpu.idle
    kernel.all.cpu.wait.total
    disk.all.total
    mem.util.cached
    mem.util.bufmem
    mem.util.free
}
[access]
disallow .* : all;
disallow :* : all;
allow local:* : enquire;
"""


def test_ros_config():
    ros_config = RosConfig(context_wrap(ROS_CONFIG_INPUT))
    ros_config_key = ros_config['log mandatory on default']
    assert ros_config is not None
    assert 'mem.util.used' in ros_config_key
    assert 'mem.physmem' in ros_config_key
    assert 'kernel.all.cpu.user' in ros_config_key
    assert 'kernel.all.cpu.sys' in ros_config_key
    assert 'kernel.all.cpu.nice' in ros_config_key
    assert 'kernel.all.cpu.steal' in ros_config_key
    assert 'kernel.all.cpu.idle' in ros_config_key
    assert 'kernel.all.cpu.wait.total' in ros_config_key
    assert 'disk.all.total' in ros_config_key
    assert 'mem.util.cached' in ros_config_key
    assert 'mem.util.bufmem' in ros_config_key
    assert 'mem.util.free' in ros_config_key
    assert list(ros_config.sections()) == ['access']
    # assert ros_config.get('access', 'disallow') == ''
