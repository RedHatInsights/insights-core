from insights.core.context import OSP
from insights.parsers.rabbitmq import RabbitMQReport
from insights.tests import context_wrap

osp_controller = OSP()
osp_controller.role = "Controller"


RABBITMQCTL_REPORT_0 = """
Error: unable to connect to node rabbit@dprcclab002: nodedown

DIAGNOSTICS
===========

attempted to contact: [rabbit@dprcclab002]

rabbit@dprcclab002:
  * connected to epmd (port 4369) on dprcclab002
  * epmd reports: node 'rabbit' not running at all
                  no other nodes on dprcclab002
  * suggestion: start the node

current node details:
- node name: 'rabbitmq-cli-08@dprcclab002'
- home dir: /var/lib/rabbitmq
- cookie hash: k0XaAkNZ29GQG22RA/Uyxw==
"""

RABBITMQCTL_REPORT_1 = """
Reporting server status on {{2016,10,17},{3,42,41}}

 ...
Status of node rabbit@rabbitmq0 ...
[{pid,5085},
 {os,{unix,linux}},
 {erlang_version,
     "Erlang R16B03-1 (erts-5.10.4) [source] [64-bit] [smp:4:4] [async-threads:30] [hipe] [kernel-poll:true]\n"},
 {listeners,[{clustering,25672,"::"},{amqp,5672,"::"}]},
 {vm_memory_high_watermark,0.4},
 {vm_memory_limit,1590132736},
 {disk_free_limit,50000000},
 {disk_free,40712921088},
 {file_descriptors,
     [{total_limit,924},{total_used,3},{sockets_limit,829},{sockets_used,1}]},
 {processes,[{limit,1048576},{used,180}]},
 {run_queue,0},
 {uptime,5590}]

Cluster status of node rabbit@rabbitmq0 ...
[{nodes,[{disc,[rabbit@rabbitmq0]}]},

Application environment of node rabbit@rabbitmq0 ...
[{auth_backends,[rabbit_auth_backend_internal]},

Permissions on /:
user    configure       write   read
guest   .*      .*      .*
redhat  redhat.*        .*      .*
redhat1 redhat.*        .*      .*

Permissions on test_vhost:

Policies on /:

Policies on test_vhost:

...done.
"""

RABBITMQCTL_REPORT_2 = """
Reporting server status on {{2016,4,26},{6,51,27}}

 ...
Status of node 'rabbit@overcloud-controller-2' ...
[{pid,4087},
 {vm_memory_limit,26943271731},
 {disk_free_limit,50000000},
 {disk_free,257304219648},
 {file_descriptors,[{total_limit,3996},
                    {total_used,835},
                    {sockets_limit,3594},
                    {sockets_used,833}]},
 {uptime,3075474}]

Cluster status of node 'rabbit@overcloud-controller-2' ...
[{nodes,[{disc,['rabbit@overcloud-controller-0',
                'rabbit@overcloud-controller-1',
                'rabbit@overcloud-controller-2']}]},
 {partitions,[]}]

Application environment of node 'rabbit@overcloud-controller-2' ...
[{auth_backends,[rabbit_auth_backend_internal]}]

Status of node 'rabbit@overcloud-controller-1' ...
[{pid,9304},
 {disk_free_limit,50000000},
 {disk_free,260561866752},
 {file_descriptors,[{total_limit,3996},
                    {total_used,853},
                    {sockets_limit,3594},
                    {sockets_used,851}]},
 {uptime,3075482}]

Cluster status of node 'rabbit@overcloud-controller-2' ...
[{nodes,[{disc,['rabbit@overcloud-controller-0',
                'rabbit@overcloud-controller-1',
                'rabbit@overcloud-controller-2']}]},
 {partitions,[]}]

Application environment of node 'rabbit@overcloud-controller-2' ...
[{auth_backends,[rabbit_auth_backend_internal]}]

Status of node 'rabbit@overcloud-controller-0' ...
[{pid,6005},
 {disk_free_limit,50000000},
 {disk_free,259739344896},
 {file_descriptors,[{total_limit,3996},
                    {total_used,967},
                    {sockets_limit,3594},
                    {sockets_used,965}]},
 {uptime,3075485}]

Cluster status of node 'rabbit@overcloud-controller-2' ...
[{nodes,[{disc,['rabbit@overcloud-controller-0',
                'rabbit@overcloud-controller-1',
                'rabbit@overcloud-controller-2']}]},
 {partitions,[]}]

Application environment of node 'rabbit@overcloud-controller-2' ...
[{auth_backends,[rabbit_auth_backend_internal]}]

Permissions on /:
user	configure	write	read
guest	.*	.*	.*

Policies on /:
vhost	name	apply-to	pattern	definition	priority
/	ha-all	all	^(?!amq\\.).*	{"ha-mode":"all"}	0

Parameters on /:

...done.
"""


def test_rabbitmq_report():
    result = RabbitMQReport(context_wrap(RABBITMQCTL_REPORT_0,
            hostname="controller_1", osp=osp_controller)).result
    assert result is None

    result = RabbitMQReport(context_wrap(RABBITMQCTL_REPORT_1,
            hostname="controller_1", osp=osp_controller)).result
    assert result.get("nstat").get("rabbit@rabbitmq0").\
            get("file_descriptors").get("total_limit") == "924"
    permissions = {'/': {'redhat1': ['redhat.*', '.*', '.*'],
                        'guest': ['.*', '.*', '.*'],
                        'redhat': ['redhat.*', '.*', '.*']},
                   'test_vhost': ''}
    assert result.get("perm") == permissions

    result = RabbitMQReport(context_wrap(RABBITMQCTL_REPORT_2,
            hostname="controller_1", osp=osp_controller)).result
    assert result.get("nstat").get("'rabbit@overcloud-controller-2'").\
            get("file_descriptors").get("total_limit") == '3996'
    assert len(result.get("nstat")) == 3
    permissions = {'/': {'guest': ['.*', '.*', '.*']}}
    assert result.get("perm") == permissions
