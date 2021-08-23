"""
RosConfig - file ``/var/lib/pcp/config/pmlogger/config.ros``
======================================================
This class provides parsing for the files:
    ``/var/lib/pcp/config/pmlogger/config.ros``

Sample input data is in the format::

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

from insights import Parser, parser
from insights.specs import Specs


@parser(Specs.ros_config)
class RosConfig(Parser):
    """Class to parse file ``config.ros``."""
    pass
