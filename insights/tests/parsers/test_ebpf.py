import doctest

from insights.parsers import ebpf
from insights.parsers.ebpf import BpftoolLinkList, BpftoolMapList, BpftoolNetList, BpftoolProgList
from insights.tests import context_wrap

BPFTOOL_LINK = """
[{"id":8,"type":"tracing","prog_id":463,"prog_type":"lsm","attach_type":"lsm_mac","target_obj_id":1,"target_btf_id":65037,"pids":[{"pid":1,"comm":"systemd"}]}]
""".strip()

BPFTOOL_MAP = """
[{"id":156,"type":"hash_of_maps","name":"cgroup_hash","flags":0,"bytes_key":8,"bytes_value":4,"max_entries":2048,"bytes_memlock":165568,"frozen":0,"pids":[{"pid":1,"comm":"systemd"}]},{"id":178,"type":"hash","flags":0,"bytes_key":4,"bytes_value":1,"max_entries":8,"bytes_memlock":2368,"frozen":0,"pids":[{"pid":229236,"comm":"NetworkManager"}]}]
""".strip()

BPFTOOL_NET = """
[{"xdp": [{"devname": "eth0","ifindex": 2,"mode": "driver","id": 125}],"tc": [{"devname": "eth0","ifindex": 2,"kind": "clsact/ingress","name": "bpf_custom.o:[classifier]","id": 140}],"flow_dissector": [],"netfilter": []}]
""".strip()

BPFTOOL_PROG = """
[{"id":463,"type":"lsm","name":"restrict_filesystems","tag":"7673068478f99ef8","gpl_compatible":true,"loaded_at":1774948458,"uid":0,"orphaned":false,"bytes_xlated":520,"jited":true,"bytes_jited":408,"bytes_memlock":4096,"map_ids":[156],"btf_id":306,"pids":[{"pid":1,"comm":"systemd"}]},{"id":564,"type":"cgroup_device","name":"sd_devices","tag":"40ddf486530245f5","gpl_compatible":true,"loaded_at":1774948492,"uid":0,"orphaned":false,"bytes_xlated":504,"jited":true,"bytes_jited":448,"bytes_memlock":4096,"pids":[{"pid":1,"comm":"systemd"}]}]
""".strip()


def test_bpftool_link():
    ret = BpftoolLinkList(context_wrap(BPFTOOL_LINK))
    assert ret[0].get('type') == 'tracing'
    assert ret[0].get('pids') == [{'pid': 1, 'comm': 'systemd'}]


def test_bpftool_map():
    ret = BpftoolMapList(context_wrap(BPFTOOL_MAP))
    assert ret[0].get('type') == 'hash_of_maps'
    assert ret[0].get('pids') == [{'pid': 1, 'comm': 'systemd'}]
    assert ret[1].get('pids') == [{'pid': 229236, 'comm': 'NetworkManager'}]


def test_bpftool_net():
    ret = BpftoolNetList(context_wrap(BPFTOOL_NET))
    assert ret[0].get('xdp')[0].get('devname') == 'eth0'
    assert ret[0].get('tc')[0].get('name') == 'bpf_custom.o:[classifier]'
    assert ret[0].get('flow_dissector') == []


def test_bpftool_prog():
    ret = BpftoolProgList(context_wrap(BPFTOOL_PROG))
    assert ret[0].get('type') == 'lsm'
    assert ret[1].get('name') == 'sd_devices'
    assert ret[1].get('pids') == [{'pid': 1, 'comm': 'systemd'}]


def test_doc_examples():
    env = {
        "bpf_link": BpftoolLinkList(context_wrap(BPFTOOL_LINK)),
        "bpf_map": BpftoolMapList(context_wrap(BPFTOOL_MAP)),
        "bpf_net": BpftoolNetList(context_wrap(BPFTOOL_NET)),
        "bpf_prog": BpftoolProgList(context_wrap(BPFTOOL_PROG)),
    }
    failed, _ = doctest.testmod(ebpf, globs=env)
    assert failed == 0
