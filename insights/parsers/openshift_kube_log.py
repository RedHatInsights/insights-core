"""
Container logs
==============

Module for parsing the log files for Openshift kubelet container logs.


ControllerManagerLog - file ``/var/log/pods/openshift-kube-controller-manager*/*/*.log``
----------------------------------------------------------------------------------------

ApiServerLog - file ``/var/log/pods/openshift-kube-apiserver*/*/*.log``
-----------------------------------------------------------------------

.. note::
    Please refer to the super-class :class:`insights.core.LogFileOutput`
"""

from insights.specs import Specs
from .. import LogFileOutput, parser


@parser(Specs.controller_manager_log)
class ControllerManagerLog(LogFileOutput):
    """Class for parsing ``/var/log/pods/openshift-kube-controller-manager*/*/*.log`` file.

    Typical content of ``*.log`` file is::

        2016-11-09 14:32:40.269 4204 WARNING oslo_reports.guru_meditation_report [-] Guru meditation now registers SIGUSR1 and SIGUSR2 by default for backward compatibility. SIGUSR1 will no longer be registered in a future release, so please use SIGUSR2 to generate reports.
        2016-11-09 14:32:40.467 4259 INFO ceilometer.declarative [-] Definitions: {'resources': [{'metrics': ['identity.authenticate.success', 'identity.authenticate.pending', 'identity.authenticate.failure', 'identity.user.created', 'identity.user.deleted', 'identity.user.updated', 'identity.group.created', 'identity.group.deleted', 'identity.group.updated', 'identity.role.created', 'identity.role.deleted', 'identity.role.updated', 'identity.project.created', 'identity.project.deleted', 'identity.project.updated', 'identity.trust.created', 'identity.trust.deleted', 'identity.role_assignment.created', 'identity.role_assignment.deleted'], 'archive_policy': 'low', 'resource_type': 'identity'}, {'metrics': ['radosgw.objects', 'radosgw.objects.size', 'radosgw.objects.containers', 'radosgw.api.request', 'radosgw.containers.objects', 'radosgw.containers.objects.size'], 'resource_type': 'ceph_account'}, {'metrics': ['instance', 'memory', 'memory.usage', 'memory.resident', 'vcpus', 'cpu', 'cpu.delta', 'cpu_util', 'disk.root.size', 'disk.ephemeral.size', 'disk.read.requests', 'disk.read.requests.rate', 'disk.write.requests', 'disk.write.requests.rate', 'disk.read.bytes', 'disk.read.bytes.rate', 'disk.write.bytes', 'disk.write.bytes.rate', 'disk.latency', 'disk.iops', 'disk.capacity', 'disk.allocation', 'disk.usage'], 'event_associated_resources': {'instance_network_interface': '{"=": {"instance_id": "%s"}}', 'instance_disk': '{"=": {"instance_id": "%s"}}'}, 'event_delete': 'compute.instance.delete.start', 'attributes': {'display_name': 'resource_metadata.display_name', 'host': 'resource_metadata.host', 'image_ref': 'resource_metadata.image_ref', 'flavor_id': 'resource_metadata.(instance_flavor_id|(flavor.id))', 'server_group': 'resource_metadata.user_metadata.server_group'}, 'event_attributes': {'id': 'payload.instance_id'}, 'resource_type': 'instance'}, {'metrics': ['network.outgoing.packets.rate', 'network.incoming.packets.rate', 'network.outgoing.packets', 'network.incoming.packets', 'network.outgoing.bytes.rate', 'network.incoming.bytes.rate', 'network.outgoing.bytes', 'network.incoming.bytes'], 'attributes': {'instance_id': 'resource_metadata.instance_id', 'name': 'resource_metadata.vnic_name'}, 'resource_type': 'instance_network_interface'}, {'metrics': ['disk.device.read.requests', 'disk.device.read.requests.rate', 'disk.device.write.requests', 'disk.device.write.requests.rate', 'disk.device.read.bytes', 'disk.device.read.bytes.rate', 'disk.device.write.bytes', 'disk.device.write.bytes.rate', 'disk.device.latency', 'disk.device.iops', 'disk.device.capacity', 'disk.device.allocation', 'disk.device.usage'], 'attributes': {'instance_id': 'resource_metadata.instance_id', 'name': 'resource_metadata.disk_name'}, 'resource_type': 'instance_disk'}, {'metrics': ['image', 'image.size', 'image.download', 'image.serve'], 'attributes': {'container_format': 'resource_metadata.container_format', 'disk_format': 'resource_metadata.disk_format', 'name': 'resource_metadata.name'}, 'event_delete': 'image.delete', 'event_attributes': {'id': 'payload.resource_id'}, 'resource_type': 'image'}, {'metrics': ['hardware.ipmi.node.power', 'hardware.ipmi.node.temperature', 'hardware.ipmi.node.inlet_temperature', 'hardware.ipmi.node.outlet_temperature', 'hardware.ipmi.node.fan', 'hardware.ipmi.node.current', 'hardware.ipmi.node.voltage', 'hardware.ipmi.node.airflow', 'hardware.ipmi.node.cups', 'hardware.ipmi.node.cpu_util', 'hardware.ipmi.node.mem_util', 'hardware.ipmi.node.io_util'], 'resource_type': 'ipmi'}, {'metrics': ['bandwidth', 'network', 'network.create', 'network.update', 'subnet', 'subnet.create', 'subnet.update', 'port', 'port.create', 'port.update', 'router', 'router.create', 'router.update', 'ip.floating', 'ip.floating.create', 'ip.floating.update'], 'resource_type': 'network'}, {'metrics': ['stack.create', 'stack.update', 'stack.delete', 'stack.resume', 'stack.suspend'], 'resource_type': 'stack'}, {'metrics': ['storage.objects.incoming.bytes', 'storage.objects.outgoing.bytes', 'storage.api.request', 'storage.objects.size', 'storage.objects', 'storage.objects.containers', 'storage.containers.objects', 'storage.containers.objects.size'], 'resource_type': 'swift_account'}, {'metrics': ['volume', 'volume.size', 'volume.create', 'volume.delete', 'volume.update', 'volume.resize', 'volume.attach', 'volume.detach'], 'attributes': {'display_name': 'resource_metadata.display_name'}, 'resource_type': 'volume'}, {'metrics': ['hardware.cpu.load.1min', 'hardware.cpu.load.5min', 'hardware.cpu.load.15min', 'hardware.cpu.util', 'hardware.memory.total', 'hardware.memory.used', 'hardware.memory.swap.total', 'hardware.memory.swap.avail', 'hardware.memory.buffer', 'hardware.memory.cached', 'hardware.network.ip.outgoing.datagrams', 'hardware.network.ip.incoming.datagrams', 'hardware.system_stats.cpu.idle', 'hardware.system_stats.io.outgoing.blocks', 'hardware.system_stats.io.incoming.blocks'], 'attributes': {'host_name': 'resource_metadata.resource_url'}, 'resource_type': 'host'}, {'metrics': ['hardware.disk.size.total', 'hardware.disk.size.used'], 'attributes': {'host_name': 'resource_metadata.resource_url', 'device_name': 'resource_metadata.device'}, 'resource_type': 'host_disk'}, {'metrics': ['hardware.network.incoming.bytes', 'hardware.network.outgoing.bytes', 'hardware.network.outgoing.errors'], 'attributes': {'host_name': 'resource_metadata.resource_url', 'device_name': 'resource_metadata.name'}, 'resource_type': 'host_network_interface'}]}
        2016-11-09 14:32:41.099 4259 WARNING oslo_config.cfg [-] Option "max_retries" from group "database" is deprecated. Use option "max_retries" from group "storage".
        2016-11-09 14:36:35.464 4204 INFO cotyledon [-] Caught SIGTERM signal, graceful exiting of master process
        2016-11-09 14:36:35.465 4259 INFO cotyledon [-] Caught signal (15) during service initialisation, delaying it
        2016-11-09 14:38:07.280 31638 WARNING oslo_reports.guru_meditation_report [-] Guru meditation now registers SIGUSR1 and SIGUSR2 by default for backward compatibility. SIGUSR1 will no longer be registered in a future release, so please use SIGUSR2 to generate reports.
    """
    pass


@parser(Specs.api_server_log)
class ApiServerLog(LogFileOutput):
    """Class for parsing ``var/log/pods/openshift-kube-apiserver*/*/*.log`` file.

    Typical content of ``*.log`` file is::

        2018-01-12 21:00:02.939 49455 INFO ceilometer.agent.manager [-] Polling pollster network.outgoing.packets in the context of some_pollsters
        2018-01-12 21:00:02.950 49455 INFO ceilometer.agent.manager [-] Polling pollster memory.usage in the context of some_pollsters
        2018-01-12 21:00:02.953 49455 WARNING ceilometer.compute.pollsters.memory [-] Cannot inspect data of MemoryUsagePollster for xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx, non-fatal reason: Failed to inspect memory usage of instance <name=instance-name1, id=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx>, can not get info from libvirt.
        2018-01-12 21:00:02.957 49455 WARNING ceilometer.compute.pollsters.memory [-] Cannot inspect data of MemoryUsagePollster for yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy, non-fatal reason: Failed to inspect memory usage of instance <name=instance-name2, id=yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy>, can not get info from libvirt.
        2018-01-12 21:00:02.963 49455 WARNING ceilometer.compute.pollsters.memory [-] Cannot inspect data of MemoryUsagePollster for zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz, non-fatal reason: Failed to inspect memory usage of instance <name=instance-name3, id=zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz>, can not get info from libvirt.
        2018-01-12 21:00:02.970 49455 INFO ceilometer.agent.manager [-] Polling pollster disk.write.requests in the context of some_pollsters
        2018-01-12 21:00:02.976 49455 INFO ceilometer.agent.manager [-] Polling pollster network.incoming.packets in the context of some_pollsters
        2018-01-12 21:00:02.981 49455 INFO ceilometer.agent.manager [-] Polling pollster cpu in the context of some_pollsters
        2018-01-12 21:00:03.014 49455 INFO ceilometer.agent.manager [-] Polling pollster network.incoming.bytes in the context of some_pollsters
        2018-01-12 21:00:03.020 49455 INFO ceilometer.agent.manager [-] Polling pollster disk.read.requests in the context of some_pollsters
        2018-01-12 21:00:03.041 49455 INFO ceilometer.agent.manager [-] Polling pollster network.outgoing.bytes in the context of some_pollsters
        2018-01-12 21:00:03.062 49455 INFO ceilometer.agent.manager [-] Polling pollster disk.write.bytes in the context of some_pollsters
    """
    pass
