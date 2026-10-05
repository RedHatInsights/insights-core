"""
eBPF Parsers
============

Parsers for eBPF relevant commands

BpftoolLinkList - Command ``bpftool link list --json``
------------------------------------------------------

BpftoolMapList - Command ``bpftool map list --json``
----------------------------------------------------

BpftoolNetList - Command ``bpftool net list --json``
----------------------------------------------------

BpftoolProgList - Command ``bpftool prog list --json``
------------------------------------------------------
"""

from insights.core import JSONParser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.bpftool_link_list)
class BpftoolLinkList(JSONParser):
    """
    Class for parsing the output of ``bpftool link list --json``.

    Typical output::

        [{"id":8,"type":"tracing","prog_id":463,"prog_type":"lsm","attach_type":"lsm_mac","target_obj_id":1,"target_btf_id":65037,"pids":[{"pid":1,"comm":"systemd"}]}]

    Examples:
        >>> type(bpf_link)
        <class 'insights.parsers.ebpf.BpftoolLinkList'>
        >>> bpf_link[0].get('id')
        8
        >>> bpf_link[0].get('pids')[0].get('comm')
        'systemd'
    """

    pass


@parser(Specs.bpftool_map_list)
class BpftoolMapList(JSONParser):
    """
    Class for parsing the output of ``bpftool map list --json``.

    Typical output::

        [{"id":156,"type":"hash_of_maps","name":"cgroup_hash","flags":0,"bytes_key":8,"bytes_value":4,"max_entries":2048,"bytes_memlock":165568,"frozen":0,"pids":[{"pid":1,"comm":"systemd"}]},{"id":178,"type":"hash","flags":0,"bytes_key":4,"bytes_value":1,"max_entries":8,"bytes_memlock":2368,"frozen":0,"pids":[{"pid":229236,"comm":"NetworkManager"}]}]

    Examples:
        >>> type(bpf_map)
        <class 'insights.parsers.ebpf.BpftoolMapList'>
        >>> bpf_map[0].get('pids')[0].get('comm')
        'systemd'
        >>> bpf_map[1].get('pids')[0].get('comm')
        'NetworkManager'
    """

    pass


@parser(Specs.bpftool_net_list)
class BpftoolNetList(JSONParser):
    """
    Class for parsing the output of ``bpftool net list --json``.

    Typical output::

        [{"xdp": [{"devname": "eth0","ifindex": 2,"mode": "driver","id": 125}],"tc": [{"devname": "eth0","ifindex": 2,"kind": "clsact/ingress","name": "bpf_custom.o:[classifier]","id": 140}],"flow_dissector": [],"netfilter": []}]

    Examples:
        >>> type(bpf_net)
        <class 'insights.parsers.ebpf.BpftoolNetList'>
        >>> bpf_net[0].get('xdp')[0].get('id')
        125
        >>> bpf_net[0].get('tc')[0].get('devname')
        'eth0'
        >>> bpf_net[0].get('netfilter')
        []
    """

    pass


@parser(Specs.bpftool_prog_list)
class BpftoolProgList(JSONParser):
    """
    Class for parsing the output of ``bpftool prog list --json``.

    Typical output::

        [{"id":463,"type":"lsm","name":"restrict_filesystems","tag":"7673068478f99ef8","gpl_compatible":true,"loaded_at":1774948458,"uid":0,"orphaned":false,"bytes_xlated":520,"jited":true,"bytes_jited":408,"bytes_memlock":4096,"map_ids":[156],"btf_id":306,"pids":[{"pid":1,"comm":"systemd"}]},{"id":564,"type":"cgroup_device","name":"sd_devices","tag":"40ddf486530245f5","gpl_compatible":true,"loaded_at":1774948492,"uid":0,"orphaned":false,"bytes_xlated":504,"jited":true,"bytes_jited":448,"bytes_memlock":4096,"pids":[{"pid":1,"comm":"systemd"}]}]

    Examples:
        >>> type(bpf_prog)
        <class 'insights.parsers.ebpf.BpftoolProgList'>
        >>> bpf_prog[0].get('id')
        463
        >>> bpf_prog[1].get('pids')[0].get('comm')
        'systemd'
    """

    pass
