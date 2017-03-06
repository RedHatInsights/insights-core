from falafel.mappers.ceph_config_show import CephCfgInfo
from falafel.tests import context_wrap

CEPHINFO = """
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
}
""".strip()


def test_cephcfginfo():
    ceph_info = CephCfgInfo(context_wrap(CEPHINFO))
    assert ceph_info.data == {
        'ms_tcp_nodelay': 'true', 'ms_max_backoff': '15', 'cluster': 'ceph',
        'ms_dispatch_throttle_bytes': '104857600', 'debug_none': '0\\/5',
        'ms_crc_data': 'true', 'perf': 'true', 'ms_tcp_prefetch_max_size':
        '4096', 'ms_die_on_bad_msg': 'false', 'ms_bind_port_max': '7300',
        'ms_bind_port_min': '6800', 'ms_die_on_skipped_message': 'false',
        'heartbeat_file': '', 'heartbeat_interval': '5',
        'heartbeat_inject_failure': '0', 'ms_crc_header': 'true',
        'max_open_files': '131072', 'ms_die_on_old_message': 'false',
        'name': 'osd.1', 'ms_type': 'simple', 'ms_initial_backoff': '0.2',
        'ms_bind_retry_delay': '5', 'ms_bind_ipv6': 'false',
        'ms_die_on_unhandled_msg': 'false', 'ms_tcp_rcvbuf': '0',
        'ms_bind_retry_count': '3'
    }
    assert ceph_info.max_open_files == '131072'
