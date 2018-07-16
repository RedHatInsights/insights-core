from insights.parsers import openshift_hosts
from insights.tests import context_wrap


OPENSHIFTHOSTS = """
[OSEv3:children]
nodes
nfs
masters
etcd

[BlankTest]

[OSEv3:vars]
openshift_master_cluster_public_hostname=None
ansible_ssh_user=root
openshift_master_cluster_hostname=None
openshift_hostname_check=false
deployment_type=openshift-enterprise

[nodes]
master.ose35.com  openshift_public_ip=192.66.208.202 openshift_ip=192.66.208.202 openshift_public_hostname=master.ose35.com openshift_hostname=master.ose35.com connect_to=master.ose35.com openshift_schedulable=False ansible_connection=local
node1.ose35.com  openshift_public_ip=192.66.208.169 openshift_ip=192.66.208.169 openshift_public_hostname=node1.ose35.com openshift_hostname=node1.ose35.com connect_to=node1.ose35.com openshift_node_labels="{'region': 'infra','zone': 'default'}" openshift_schedulable=True
node2.ose35.com  openshift_public_ip=192.66.208.170 openshift_ip=192.66.208.170 openshift_public_hostname=node2.ose35.com openshift_hostname=node2.ose35.com connect_to=node2.ose35.com openshift_node_labels="{'region': 'infra','zone': 'default'}" openshift_schedulable=True

[nfs]
master.ose35.com  openshift_public_ip=192.66.208.202 openshift_ip=192.66.208.202 openshift_public_hostname=master.ose35.com openshift_hostname=master.ose35.com connect_to=master.ose35.com ansible_connection=local

[masters]
master.ose35.com  openshift_public_ip=192.66.208.202 openshift_ip=192.66.208.202 openshift_public_hostname=master.ose35.com openshift_hostname=master.ose35.com connect_to=master.ose35.com ansible_connection=local

[etcd]
master.ose35.com  openshift_public_ip=192.66.208.202 openshift_ip=192.66.208.202 openshift_public_hostname=master.ose35.com openshift_hostname=master.ose35.com connect_to=master.ose35.com ansible_connection=local
""".strip()


def test_openshifthosts():
    host_info = openshift_hosts.OpenShiftHosts(context_wrap(OPENSHIFTHOSTS))
    assert host_info["OSEv3:children"] == ["nodes", "nfs", "masters", "etcd"]
    assert host_info["OSEv3:vars"]["ansible_ssh_user"] == "root"
    assert host_info["nodes"]["master.ose35.com"]["openshift_public_ip"] == "192.66.208.202"
    assert host_info["nodes"]["node1.ose35.com"]["openshift_node_labels"] == {'region': 'infra', 'zone': 'default'}
    assert host_info.has_node("node1.ose35.com")
    assert not host_info.has_var("openshift_use_crio")
    assert host_info.has_node_type("etcd")
    assert host_info["BlankTest"] == {}
