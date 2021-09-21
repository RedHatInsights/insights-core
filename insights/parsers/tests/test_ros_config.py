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
    assert ros_config.specs[0].get('state') == 'mandatory on'
    assert ros_config.specs[0].get('metrics') == {'mem.util.used': [],
                                                  'mem.physmem': [],
                                                  'kernel.all.cpu.user': [],
                                                  'kernel.all.cpu.sys': [],
                                                  'kernel.all.cpu.nice': [],
                                                  'kernel.all.cpu.steal': [],
                                                  'kernel.all.cpu.idle': [],
                                                  'kernel.all.cpu.wait.total': [],
                                                  'disk.all.total': [],
                                                  'mem.util.cached': [],
                                                  'mem.util.bufmem': [],
                                                  'mem.util.free': []}
    assert ros_config.specs[0].get('logging_interval') == 'default'
    assert ros_config.rules == [
                                {
                                    'allow_disallow': 'disallow',
                                    'hostlist': ['.*'],
                                    'operationlist': ['all']
                                },
                                {
                                    'allow_disallow': 'disallow',
                                    'hostlist': [':*'],
                                    'operationlist': ['all']
                                },
                                {
                                    'allow_disallow': 'allow',
                                    'hostlist': ['local:*'],
                                    'operationlist': ['enquire']
                                }
                               ]
