"""
ceph daemon {ceph_socket_files} config show - Command
=====================================================

This mapper reads the output of the command ``ceph daemon .. config show``
and parses it into a dictionary, keyed on the left hand column of
the "ceph daemon config show" output.

The specs handled by this command inlude::

    "ceph_config_show"          : CommandSpec("/usr/bin/ceph daemon {ceph_socket_files} config show", ceph_socket_files=r"\S+"),

Sample output of the command::

    {
        "name": "osd.1",
        "cluster": "ceph",
        "debug_none": "0\/5",
        "heartbeat_interval": "5",
        "heartbeat_file": "",
        "heartbeat_inject_failure": "0",
        "perf": "true",
        "max_open_files": "131072",
        "ms_type": "simple",
        "ms_tcp_nodelay": "true",
        "ms_tcp_rcvbuf": "0",
        "ms_tcp_prefetch_max_size": "4096",
        "ms_initial_backoff": "0.2",
        "ms_max_backoff": "15",
        "ms_crc_data": "true",
        "ms_crc_header": "true",
        "ms_die_on_bad_msg": "false",
        "ms_die_on_unhandled_msg": "false",
        "ms_die_on_old_message": "false",
        "ms_die_on_skipped_message": "false",
        "ms_dispatch_throttle_bytes": "104857600",
        "ms_bind_ipv6": "false",
        "ms_bind_port_min": "6800",
        "ms_bind_port_max": "7300",
        "ms_bind_retry_count": "3",
        "ms_bind_retry_delay": "5",
        ...
        ...
    }


Examples:

    >>> from falafel.tests import context_wrap
    >>> from falafel.mappers.ceph_config_show import CephCfgInfo
    >>> ceph_info = CephCfgInfo(context_wrap(CEPHINFO))
    >>> cpu_info.max_open_files
    131072
"""

import shlex
from .. import Mapper, mapper, get_active_lines, LegacyItemAccess


@mapper('ceph_config_show')
class CephCfgInfo(LegacyItemAccess, Mapper):
    """
    Parse the output of the command "ceph daemon .. config show" to get
    a mapping table of configuration parameters and values at osd runtime.
    """

    def parse_content(self, content):
        self.data = {}
        for line in get_active_lines(content):
            if line.startswith('{') or line.startswith('}'):
                continue

            key, value = shlex.split(line.replace(',', ''))
            key = key.replace(':', '')
            self.data[key] = value

    @property
    def max_open_files(self):
        """
        str: Return the value of max_open_files
        """
        return self.data["max_open_files"]
