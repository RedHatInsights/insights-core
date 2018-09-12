import doctest
from insights.parsers import ceph_log
from insights.parsers.ceph_log import CephLog
from insights.tests import context_wrap

from datetime import datetime


CEPH_LOG = """
2017-05-31 13:01:44.034376 mon.0 192.xx.xx.xx:6789/0 742585 : cluster [INF] pgmap v5133969: 320 pgs: 3 active+clean+scrubbing+deep, 317 active+clean; 898 GB data, 1828 GB used, 48447 GB / 50275 GB avail; 2027 kB/s rd, 20215 kB/s wr, 711 op/s
2017-05-31 13:01:45.041760 mon.0 192.xx.xx.xx:6789/0 742586 : cluster [INF] pgmap v5133970: 320 pgs: 3 active+clean+scrubbing+deep, 317 active+clean; 898 GB data, 1828 GB used, 48447 GB / 50275 GB avail; 1606 kB/s rd, 17354 kB/s wr, 718 op/s
2017-05-31 13:01:46.933829 osd.22 192.xx.xx.xx:6814/42154 172581 : cluster [WRN] 44 slow requests, 2 included below; oldest blocked for > 49.982746 secs
2017-05-31 13:01:46.933946 osd.22 192.xx.xx.xx:6814/42154 172582 : cluster [WRN] slow request 30.602517 seconds old, received at 2017-05-31 13:01:06.330484: osd_op(client.3395798.0:2855671 1.54392173 gnocchi_06c8214c-afae-4e64-8a4a-a466c4f257dc_1244160000.0_median_86400.0_v3 [write 26253~9] snapc 0=[] ondisk+write+known_if_redirected e487) currently waiting for subops from 23
2017-05-31 13:01:46.933955 osd.22 192.xx.xx.xx:6814/42154 172583 : cluster [WRN] slow request 30.530961 seconds old, received at 2017-05-31 13:01:06.402041: osd_op(client.324182.0:46141816 1.e637a4b3 measure [omap-rm-keys 0~107] snapc 0=[] ondisk+write+skiprwlocks+known_if_redirected e487) currently waiting for subops from 23
2017-05-31 13:01:47.050539 mon.0 192.xx.xx.xx:6789/0 742589 : cluster [INF] pgmap v5133971: 320 pgs: 3 active+clean+scrubbing+deep, 317 active+clean; 898 GB data, 1828 GB used, 48447 GB / 50275 GB avail; 1597 kB/s rd, 7259 kB/s wr, 398 op/s
2017-05-31 13:01:48.057187 mon.0 192.xx.xx.xx:6789/0 742590 : cluster [INF] pgmap v5133972: 320 pgs: 3 active+clean+scrubbing+deep, 317 active+clean; 898 GB data, 1828 GB used, 48447 GB / 50275 GB avail; 2373 kB/s rd, 5138 kB/s wr, 354 op/s
2017-05-31 13:01:49.064950 mon.0 192.xx.xx.xx:6789/0 742598 : cluster [INF] pgmap v5133973: 320 pgs: 3 active+clean+scrubbing+deep, 317 active+clean; 898 GB data, 1828 GB used, 48447 GB / 50275 GB avail; 4187 kB/s rd, 10266 kB/s wr, 714 op/s
2017-05-31 13:01:50.069437 mon.0 192.xx.xx.xx:6789/0 742599 : cluster [INF] pgmap v5133974: 320 pgs: 3 active+clean+scrubbing+deep, 317 active+clean; 898 GB data, 1828 GB used, 48447 GB / 50275 GB avail; 470 MB/s rd, 11461 kB/s wr, 786 op/s
""".strip()


def test_ceph_log():
    ceph_logs = CephLog(context_wrap(CEPH_LOG))
    assert len(ceph_logs.get("[WRN] slow request")) == 2
    assert len(list(ceph_logs.get_after(datetime(2017, 5, 31, 13, 1, 46)))) == 7
    assert len(ceph_logs.get("[INF]")) == 6
    assert "slow requests" in ceph_logs


def test_doc():
    env = {"ceph_log": CephLog(context_wrap(CEPH_LOG, path="/var/log/ceph/ceph.log"))}
    failed, total = doctest.testmod(ceph_log, globs=env)
    assert failed == 0
