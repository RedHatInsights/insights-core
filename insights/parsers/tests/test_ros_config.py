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
    print(ros_config.data)
    assert ros_config.data is not None

    flatlist = [element for sublist in ros_config.data for element in sublist]
    metrics = flatlist[0][1]
    assert flatlist[1] == '[access]'
    assert 'mem.util.used' in metrics
    assert 'mem.physmem' in metrics
    assert 'kernel.all.cpu.user' in metrics
    assert 'kernel.all.cpu.sys' in metrics
    assert 'kernel.all.cpu.nice' in metrics
    assert 'kernel.all.cpu.steal' in metrics
    assert 'kernel.all.cpu.idle' in metrics
    assert 'kernel.all.cpu.wait.total' in metrics
    assert 'disk.all.total' in metrics
    assert 'mem.util.cached' in metrics
    assert 'mem.util.bufmem' in metrics
    assert 'mem.util.free' in metrics
    for item in flatlist[2]:
        assert item[0] == 'allow' or 'disallow'
        assert isinstance(item[1], list)
        assert item[2] == ':'
        assert isinstance(item[3], list)
