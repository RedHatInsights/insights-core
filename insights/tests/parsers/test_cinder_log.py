from insights.parsers.cinder_log import CinderApiLog, CinderVolumeLog
from insights.tests import context_wrap

from datetime import datetime

api_log = """
2019-04-16 21:01:02.072 21 INFO cinder.api.openstack.wsgi [req-e7b42a20-4109-45b7-b18a-ae5ad4831909 - - - - -] OPTIONS http://controller-0.internalapi.localdomain/
2019-04-16 21:01:02.073 21 DEBUG cinder.api.openstack.wsgi [req-e7b42a20-4109-45b7-b18a-ae5ad4831909 - - - - -] Empty body provided in request get_body /usr/lib/python2.7/site-packages/cinder/api/openstack/wsgi.py:718
2019-04-16 21:01:02.073 21 DEBUG cinder.api.openstack.wsgi [req-e7b42a20-4109-45b7-b18a-ae5ad4831909 - - - - -] Calling method '<bound method VersionsController.all of <cinder.api.versions.VersionsController object at 0x7f44fe7ee1d0>>' _process_stack /usr/lib/python2.7/site-packages/cinder/api/openstack/wsgi.py:871
2019-04-16 21:01:02.074 21 INFO cinder.api.openstack.wsgi [req-e7b42a20-4109-45b7-b18a-ae5ad4831909 - - - - -] http://controller-0.internalapi.localdomain/ returned with HTTP 300
2019-04-16 21:01:04.079 22 INFO cinder.api.openstack.wsgi [req-43db684e-f4eb-4b23-9f8e-82beb95ab0b7 - - - - -] OPTIONS http://controller-0.internalapi.localdomain/
"""

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


def test_cinder_api_log():
    log = CinderApiLog(context_wrap(api_log))
    assert len(log.get(["req-"])) == 5
    assert len(log.get("e7b42a20-4109-45b7-b18a-ae5ad4831909")) == 4
    assert len(list(log.get_after(datetime(2019, 4, 16, 21, 0, 0)))) == 5


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
