#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
Ceilometer logs
===============

Module for parsing the log files for Ceilometer

CeilometerCentralLog - file ``/var/log/ceilometer/central.log``
---------------------------------------------------------------

CeilometerCollectorLog - file ``/var/log/ceilometer/collector.log``
-------------------------------------------------------------------

CeilometerComputeLog - file ``/var/log/ceilometer/compute.log``
---------------------------------------------------------------

.. note::
    Please refer to the super-class :class:`insights.core.LogFileOutput`

"""

from .. import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.ceilometer_central_log)
class CeilometerCentralLog(LogFileOutput):
    """Class for parsing ``/var/log/ceilometer/central.log`` file.

    Typical content of ``central.log`` file is::

        2016-11-09 14:38:08.484 31654 WARNING oslo_reports.guru_meditation_report [-] Guru meditation now registers SIGUSR1 and SIGUSR2 by default for backward compatibility. SIGUSR1 will no longer be registered in a future release, so please use SIGUSR2 to generate reports.
        2016-11-09 14:38:09.711 31723 INFO ceilometer.declarative [-] Definitions: {'metric': [{'snmp_inspector': {'oid': '1.3.6.1.4.1.2021.10.1.3.1', 'type': 'lambda x: float(str(x))', 'matching_type': 'type_exact'}, 'type': 'gauge', 'name': 'hardware.cpu.load.1min', 'unit': 'process'}, {'snmp_inspector': {'oid': '1.3.6.1.4.1.2021.10.1.3.2', 'type': 'lambda x: float(str(x))', 'matching_type': 'type_exact'}, 'type': 'gauge', 'name': 'hardware.cpu.load.5min', 'unit': 'process'}, {'snmp_inspector': {'oid': '1.3.6.1.4.1.2021.10.1.3.3', 'type': 'lambda x: float(str(x))', 'matching_type': 'type_exact'}, 'type': 'gauge', 'name': 'hardware.cpu.load.15min', 'unit': 'process'}, {'snmp_inspector': {'oid': '1.3.6.1.4.1.2021.11.9.0', 'type': 'int', 'matching_type': 'type_exact'}, 'type': 'gauge', 'name': 'hardware.cpu.util', 'unit': '%'}, {'snmp_inspector': {'post_op': '_post_op_disk', 'oid': '1.3.6.1.4.1.2021.9.1.6', 'type': 'int', 'matching_type': 'type_prefix', 'metadata': {'device': {'oid': '1.3.6.1.4.1.2021.9.1.3', 'type': 'str'}, 'path': {'oid': '1.3.6.1.4.1.2021.9.1.2', 'type': 'str'}}}, 'type': 'gauge', 'name': 'hardware.disk.size.total', 'unit': 'KB'}, {'snmp_inspector': {'post_op': '_post_op_disk', 'oid': '1.3.6.1.4.1.2021.9.1.8', 'type': 'int', 'matching_type': 'type_prefix', 'metadata': {'device': {'oid': '1.3.6.1.4.1.2021.9.1.3', 'type': 'str'}, 'path': {'oid': '1.3.6.1.4.1.2021.9.1.2', 'type': 'str'}}}, 'type': 'gauge', 'name': 'hardware.disk.size.used', 'unit': 'KB'}, {'snmp_inspector': {'oid': '1.3.6.1.4.1.2021.4.5.0', 'type': 'int', 'matching_type': 'type_exact'}, 'type': 'gauge', 'name': 'hardware.memory.total', 'unit': 'KB'}, {'snmp_inspector': {'oid': '1.3.6.1.4.1.2021.4.6.0', 'type': 'int', 'matching_type': 'type_exact', 'post_op': '_post_op_memory_avail_to_used'}, 'type': 'gauge', 'name': 'hardware.memory.used', 'unit': 'KB'}, {'snmp_inspector': {'oid': '1.3.6.1.4.1.2021.4.3.0', 'type': 'int', 'matching_type': 'type_exact'}, 'type': 'gauge', 'name': 'hardware.memory.swap.total', 'unit': 'KB'}, {'snmp_inspector': {'oid': '1.3.6.1.4.1.2021.4.4.0', 'type': 'int', 'matching_type': 'type_exact'}, 'type': 'gauge', 'name': 'hardware.memory.swap.avail', 'unit': 'KB'}, {'snmp_inspector': {'oid': '1.3.6.1.4.1.2021.4.14.0', 'type': 'int', 'matching_type': 'type_exact'}, 'type': 'gauge', 'name': 'hardware.memory.buffer', 'unit': 'KB'}, {'snmp_inspector': {'oid': '1.3.6.1.4.1.2021.4.15.0', 'type': 'int', 'matching_type': 'type_exact'}, 'type': 'gauge', 'name': 'hardware.memory.cached', 'unit': 'KB'}, {'snmp_inspector': {'post_op': '_post_op_net', 'oid': '1.3.6.1.2.1.2.2.1.10', 'type': 'int', 'matching_type': 'type_prefix', 'metadata': {'mac': {'oid': '1.3.6.1.2.1.2.2.1.6', 'type': "lambda x: x.prettyPrint().replace('0x', '')"}, 'speed': {'oid': '1.3.6.1.2.1.2.2.1.5', 'type': 'lambda x: int(x) / 8'}, 'name': {'oid': '1.3.6.1.2.1.2.2.1.2', 'type': 'str'}}}, 'type': 'cumulative', 'name': 'hardware.network.incoming.bytes', 'unit': 'B'}, {'snmp_inspector': {'post_op': '_post_op_net', 'oid': '1.3.6.1.2.1.2.2.1.16', 'type': 'int', 'matching_type': 'type_prefix', 'metadata': {'mac': {'oid': '1.3.6.1.2.1.2.2.1.6', 'type': "lambda x: x.prettyPrint().replace('0x', '')"}, 'speed': {'oid': '1.3.6.1.2.1.2.2.1.5', 'type': 'lambda x: int(x) / 8'}, 'name': {'oid': '1.3.6.1.2.1.2.2.1.2', 'type': 'str'}}}, 'type': 'cumulative', 'name': 'hardware.network.outgoing.bytes', 'unit': 'B'}, {'snmp_inspector': {'post_op': '_post_op_net', 'oid': '1.3.6.1.2.1.2.2.1.20', 'type': 'int', 'matching_type': 'type_prefix', 'metadata': {'mac': {'oid': '1.3.6.1.2.1.2.2.1.6', 'type': "lambda x: x.prettyPrint().replace('0x', '')"}, 'speed': {'oid': '1.3.6.1.2.1.2.2.1.5', 'type': 'lambda x: int(x) / 8'}, 'name': {'oid': '1.3.6.1.2.1.2.2.1.2', 'type': 'str'}}}, 'type': 'cumulative', 'name': 'hardware.network.outgoing.errors', 'unit': 'packet'}, {'snmp_inspector': {'oid': '1.3.6.1.2.1.4.10.0', 'type': 'int', 'matching_type': 'type_exact'}, 'type': 'cumulative', 'name': 'hardware.network.ip.outgoing.datagrams', 'unit': 'datagrams'}, {'snmp_inspector': {'oid': '1.3.6.1.2.1.4.3.0', 'type': 'int', 'matching_type': 'type_exact'}, 'type': 'cumulative', 'name': 'hardware.network.ip.incoming.datagrams', 'unit': 'datagrams'}, {'snmp_inspector': {'oid': '1.3.6.1.4.1.2021.11.11.0', 'type': 'int', 'matching_type': 'type_exact'}, 'type': 'gauge', 'name': 'hardware.system_stats.cpu.idle', 'unit': '%'}, {'snmp_inspector': {'oid': '1.3.6.1.4.1.2021.11.57.0', 'type': 'int', 'matching_type': 'type_exact'}, 'type': 'cumulative', 'name': 'hardware.system_stats.io.outgoing.blocks', 'unit': 'blocks'}, {'snmp_inspector': {'oid': '1.3.6.1.4.1.2021.11.58.0', 'type': 'int', 'matching_type': 'type_exact'}, 'type': 'cumulative', 'name': 'hardware.system_stats.io.incoming.blocks', 'unit': 'blocks'}]}
        2016-11-09 14:38:09.986 31723 WARNING oslo_config.cfg [-] Option "rpc_backend" from group "DEFAULT" is deprecated for removal.  Its value may be silently ignored in the future.
        2016-11-09 14:38:10.040 31723 INFO ceilometer.pipeline [-] Config file: {'sources': [{'interval': 600, 'meters': ['*'], 'name': 'meter_source', 'sinks': ['meter_sink']}, {'interval': 600, 'meters': ['cpu'], 'name': 'cpu_source', 'sinks': ['cpu_sink', 'cpu_delta_sink']}, {'interval': 600, 'meters': ['disk.read.bytes', 'disk.read.requests', 'disk.write.bytes', 'disk.write.requests', 'disk.device.read.bytes', 'disk.device.read.requests', 'disk.device.write.bytes', 'disk.device.write.requests'], 'name': 'disk_source', 'sinks': ['disk_sink']}, {'interval': 600, 'meters': ['network.incoming.bytes', 'network.incoming.packets', 'network.outgoing.bytes', 'network.outgoing.packets'], 'name': 'network_source', 'sinks': ['network_sink']}], 'sinks': [{'publishers': ['notifier://'], 'transformers': None, 'name': 'meter_sink'}, {'publishers': ['notifier://'], 'transformers': [{'name': 'rate_of_change', 'parameters': {'target': {'scale': '100.0 / (10**9 * (resource_metadata.cpu_number or 1))', 'type': 'gauge', 'name': 'cpu_util', 'unit': '%'}}}], 'name': 'cpu_sink'}, {'publishers': ['notifier://'], 'transformers': [{'name': 'delta', 'parameters': {'target': {'name': 'cpu.delta'}, 'growth_only': True}}], 'name': 'cpu_delta_sink'}, {'publishers': ['notifier://'], 'transformers': [{'name': 'rate_of_change', 'parameters': {'source': {'map_from': {'name': '(disk\\.device|disk)\\.(read|write)\\.(bytes|requests)', 'unit': '(B|request)'}}, 'target': {'map_to': {'name': '\\1.\\2.\\3.rate', 'unit': '\\1/s'}, 'type': 'gauge'}}}], 'name': 'disk_sink'}, {'publishers': ['notifier://'], 'transformers': [{'name': 'rate_of_change', 'parameters': {'source': {'map_from': {'name': 'network\\.(incoming|outgoing)\\.(bytes|packets)', 'unit': '(B|packet)'}}, 'target': {'map_to': {'name': 'network.\\1.\\2.rate', 'unit': '\\1/s'}, 'type': 'gauge'}}}], 'name': 'network_sink'}]}
        2016-11-09 14:38:10.041 31723 INFO ceilometer.pipeline [-] detected decoupled pipeline config format
        2016-11-09 14:38:10.053 31723 INFO ceilometer.coordination [-] Coordination backend started successfully.
        2016-11-09 14:38:10.064 31723 INFO ceilometer.coordination [-] Joined partitioning group central-global
        2016-11-09 14:58:10.621 31723 INFO ceilometer.agent.manager [-] Skip pollster switch, no resources found this cycle
        2016-11-09 14:58:15.655 31723 INFO ceilometer.agent.manager [-] Skip pollster hardware.memory.used, no resources found this cycle
        2016-11-09 14:58:15.656 31723 INFO ceilometer.agent.manager [-] Skip pollster switch.port, no resources found this cycle
        2016-11-09 14:58:15.657 31723 INFO ceilometer.agent.manager [-] Skip pollster switch.port.receive.bytes, no resources found this cycle
        2016-11-09 14:58:15.657 31723 INFO ceilometer.agent.manager [-] Skip pollster hardware.system_stats.io.incoming.blocks, no resources found this cycle
        2016-11-09 14:58:17.027 31723 WARNING ceilometer.neutron_client [-] The resource could not be found.
    """
    pass


@parser(Specs.ceilometer_collector_log)
class CeilometerCollectorLog(LogFileOutput):
    """Class for parsing ``/var/log/ceilometer/collector.log`` file.

    Typical content of ``collector.log`` file is::

        2016-11-09 14:32:40.269 4204 WARNING oslo_reports.guru_meditation_report [-] Guru meditation now registers SIGUSR1 and SIGUSR2 by default for backward compatibility. SIGUSR1 will no longer be registered in a future release, so please use SIGUSR2 to generate reports.
        2016-11-09 14:32:40.467 4259 INFO ceilometer.declarative [-] Definitions: {'resources': [{'metrics': ['identity.authenticate.success', 'identity.authenticate.pending', 'identity.authenticate.failure', 'identity.user.created', 'identity.user.deleted', 'identity.user.updated', 'identity.group.created', 'identity.group.deleted', 'identity.group.updated', 'identity.role.created', 'identity.role.deleted', 'identity.role.updated', 'identity.project.created', 'identity.project.deleted', 'identity.project.updated', 'identity.trust.created', 'identity.trust.deleted', 'identity.role_assignment.created', 'identity.role_assignment.deleted'], 'archive_policy': 'low', 'resource_type': 'identity'}, {'metrics': ['radosgw.objects', 'radosgw.objects.size', 'radosgw.objects.containers', 'radosgw.api.request', 'radosgw.containers.objects', 'radosgw.containers.objects.size'], 'resource_type': 'ceph_account'}, {'metrics': ['instance', 'memory', 'memory.usage', 'memory.resident', 'vcpus', 'cpu', 'cpu.delta', 'cpu_util', 'disk.root.size', 'disk.ephemeral.size', 'disk.read.requests', 'disk.read.requests.rate', 'disk.write.requests', 'disk.write.requests.rate', 'disk.read.bytes', 'disk.read.bytes.rate', 'disk.write.bytes', 'disk.write.bytes.rate', 'disk.latency', 'disk.iops', 'disk.capacity', 'disk.allocation', 'disk.usage'], 'event_associated_resources': {'instance_network_interface': '{"=": {"instance_id": "%s"}}', 'instance_disk': '{"=": {"instance_id": "%s"}}'}, 'event_delete': 'compute.instance.delete.start', 'attributes': {'display_name': 'resource_metadata.display_name', 'host': 'resource_metadata.host', 'image_ref': 'resource_metadata.image_ref', 'flavor_id': 'resource_metadata.(instance_flavor_id|(flavor.id))', 'server_group': 'resource_metadata.user_metadata.server_group'}, 'event_attributes': {'id': 'payload.instance_id'}, 'resource_type': 'instance'}, {'metrics': ['network.outgoing.packets.rate', 'network.incoming.packets.rate', 'network.outgoing.packets', 'network.incoming.packets', 'network.outgoing.bytes.rate', 'network.incoming.bytes.rate', 'network.outgoing.bytes', 'network.incoming.bytes'], 'attributes': {'instance_id': 'resource_metadata.instance_id', 'name': 'resource_metadata.vnic_name'}, 'resource_type': 'instance_network_interface'}, {'metrics': ['disk.device.read.requests', 'disk.device.read.requests.rate', 'disk.device.write.requests', 'disk.device.write.requests.rate', 'disk.device.read.bytes', 'disk.device.read.bytes.rate', 'disk.device.write.bytes', 'disk.device.write.bytes.rate', 'disk.device.latency', 'disk.device.iops', 'disk.device.capacity', 'disk.device.allocation', 'disk.device.usage'], 'attributes': {'instance_id': 'resource_metadata.instance_id', 'name': 'resource_metadata.disk_name'}, 'resource_type': 'instance_disk'}, {'metrics': ['image', 'image.size', 'image.download', 'image.serve'], 'attributes': {'container_format': 'resource_metadata.container_format', 'disk_format': 'resource_metadata.disk_format', 'name': 'resource_metadata.name'}, 'event_delete': 'image.delete', 'event_attributes': {'id': 'payload.resource_id'}, 'resource_type': 'image'}, {'metrics': ['hardware.ipmi.node.power', 'hardware.ipmi.node.temperature', 'hardware.ipmi.node.inlet_temperature', 'hardware.ipmi.node.outlet_temperature', 'hardware.ipmi.node.fan', 'hardware.ipmi.node.current', 'hardware.ipmi.node.voltage', 'hardware.ipmi.node.airflow', 'hardware.ipmi.node.cups', 'hardware.ipmi.node.cpu_util', 'hardware.ipmi.node.mem_util', 'hardware.ipmi.node.io_util'], 'resource_type': 'ipmi'}, {'metrics': ['bandwidth', 'network', 'network.create', 'network.update', 'subnet', 'subnet.create', 'subnet.update', 'port', 'port.create', 'port.update', 'router', 'router.create', 'router.update', 'ip.floating', 'ip.floating.create', 'ip.floating.update'], 'resource_type': 'network'}, {'metrics': ['stack.create', 'stack.update', 'stack.delete', 'stack.resume', 'stack.suspend'], 'resource_type': 'stack'}, {'metrics': ['storage.objects.incoming.bytes', 'storage.objects.outgoing.bytes', 'storage.api.request', 'storage.objects.size', 'storage.objects', 'storage.objects.containers', 'storage.containers.objects', 'storage.containers.objects.size'], 'resource_type': 'swift_account'}, {'metrics': ['volume', 'volume.size', 'volume.create', 'volume.delete', 'volume.update', 'volume.resize', 'volume.attach', 'volume.detach'], 'attributes': {'display_name': 'resource_metadata.display_name'}, 'resource_type': 'volume'}, {'metrics': ['hardware.cpu.load.1min', 'hardware.cpu.load.5min', 'hardware.cpu.load.15min', 'hardware.cpu.util', 'hardware.memory.total', 'hardware.memory.used', 'hardware.memory.swap.total', 'hardware.memory.swap.avail', 'hardware.memory.buffer', 'hardware.memory.cached', 'hardware.network.ip.outgoing.datagrams', 'hardware.network.ip.incoming.datagrams', 'hardware.system_stats.cpu.idle', 'hardware.system_stats.io.outgoing.blocks', 'hardware.system_stats.io.incoming.blocks'], 'attributes': {'host_name': 'resource_metadata.resource_url'}, 'resource_type': 'host'}, {'metrics': ['hardware.disk.size.total', 'hardware.disk.size.used'], 'attributes': {'host_name': 'resource_metadata.resource_url', 'device_name': 'resource_metadata.device'}, 'resource_type': 'host_disk'}, {'metrics': ['hardware.network.incoming.bytes', 'hardware.network.outgoing.bytes', 'hardware.network.outgoing.errors'], 'attributes': {'host_name': 'resource_metadata.resource_url', 'device_name': 'resource_metadata.name'}, 'resource_type': 'host_network_interface'}]}
        2016-11-09 14:32:41.099 4259 WARNING oslo_config.cfg [-] Option "max_retries" from group "database" is deprecated. Use option "max_retries" from group "storage".
        2016-11-09 14:36:35.464 4204 INFO cotyledon [-] Caught SIGTERM signal, graceful exiting of master process
        2016-11-09 14:36:35.465 4259 INFO cotyledon [-] Caught signal (15) during service initialisation, delaying it
        2016-11-09 14:38:07.280 31638 WARNING oslo_reports.guru_meditation_report [-] Guru meditation now registers SIGUSR1 and SIGUSR2 by default for backward compatibility. SIGUSR1 will no longer be registered in a future release, so please use SIGUSR2 to generate reports.
    """
    pass


@parser(Specs.ceilometer_compute_log)
class CeilometerComputeLog(LogFileOutput):
    """Class for parsing ``/var/log/ceilometer/compute.log`` file.

    Typical content of ``compute.log`` file is::

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
