from insights.parsers import ros_config
from insights.tests import context_wrap
import doctest


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
    ros_input = ros_config.RosConfig(context_wrap(ROS_CONFIG_INPUT))
    assert ros_input.data is not None
    assert ros_input.specs[0].get('state') == 'mandatory on'
    assert ros_input.specs[0].get('metrics') == {'mem.util.used': [],
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
    assert ros_input.specs[0].get('logging_interval') == 'default'
    assert ros_input.rules == [
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


def test_ros_config_documentation():
    env = {
        'ros_input': ros_config.RosConfig(context_wrap(ROS_CONFIG_INPUT, path='/var/lib/pcp/config/pmlogger/config.ros')),
    }
    failed, total = doctest.testmod(ros_config, globs=env)
    assert failed == 0
