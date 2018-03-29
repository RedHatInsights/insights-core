from insights.parsers.cinder_log import CinderVolumeLog
from insights.tests import context_wrap

from datetime import datetime

CINDER_LOG = """
2015-06-19 07:31:41.020 7947 DEBUG cinder.openstack.common.periodic_task [-] Running periodic task VolumeManager._publish_service_capabilities run_periodic_tasks /usr/lib/python2.7/site-packages/cinder/openstack/common/periodic_task.py:178
2015-06-19 07:31:41.022 7947 DEBUG cinder.manager [-] Notifying Schedulers of capabilities ... _publish_service_capabilities /usr/lib/python2.7/site-packages/cinder/manager.py:128
2015-06-19 07:31:41.025 7947 DEBUG cinder.openstack.common.periodic_task [-] Running periodic task VolumeManager._report_driver_status run_periodic_tasks /usr/lib/python2.7/site-packages/cinder/openstack/common/periodic_task.py:178
2015-06-19 07:31:41.026 7947 INFO cinder.volume.manager [-] Updating volume status
2015-11-27 11:22:45.416 16656 INFO oslo.messaging._drivers.impl_rabbit [-] Connecting to AMQP server on 169.254.10.22:5672
2015-11-27 11:22:45.426 16656 INFO oslo.messaging._drivers.impl_rabbit [-] Connected to AMQP server on 169.254.10.22:5672
2015-11-27 11:23:07.146 16656 INFO cinder.volume.manager [req-a8c22cdb-e21b-497f-affe-9380478decae - - - - -] Updating volume status
2015-11-27 11:23:07.148 16656 WARNING cinder.volume.manager [req-a8c22cdb-e21b-497f-affe-9380478decae - - - - -] Unable to update stats, LVMISCSIDriver -2.0.0 (config name rbd) driver is uninitialized.
"""


def test_get_cinder_log():
    log = CinderVolumeLog(context_wrap(CINDER_LOG))
    assert len(log.lines) == 8
    assert sorted([i['raw_message'] for i in log.get('cinder.volume.manager')]) == sorted([
        '2015-06-19 07:31:41.026 7947 INFO cinder.volume.manager [-] Updating volume status',
        '2015-11-27 11:23:07.146 16656 INFO cinder.volume.manager [req-a8c22cdb-e21b-497f-affe-9380478decae - - - - -] Updating volume status',
        '2015-11-27 11:23:07.148 16656 WARNING cinder.volume.manager [req-a8c22cdb-e21b-497f-affe-9380478decae - - - - -] Unable to update stats, LVMISCSIDriver -2.0.0 (config name rbd) driver is uninitialized.',
    ])

    assert sorted([i['raw_message'] for i in list(log.get_after(datetime(2015, 11, 27, 11, 23, 0)))]) == sorted([
        '2015-11-27 11:23:07.146 16656 INFO cinder.volume.manager [req-a8c22cdb-e21b-497f-affe-9380478decae - - - - -] Updating volume status',
        '2015-11-27 11:23:07.148 16656 WARNING cinder.volume.manager [req-a8c22cdb-e21b-497f-affe-9380478decae - - - - -] Unable to update stats, LVMISCSIDriver -2.0.0 (config name rbd) driver is uninitialized.',
    ])
