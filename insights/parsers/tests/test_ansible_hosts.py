import doctest
from insights.parsers import ansible_hosts
from insights.parsers.ansible_hosts import AnsibleHosts
from insights.tests import context_wrap


ANSIBLE_HOSTS = """
mail.example.com
jumper ansible_port=5555  ansible_host=192.0.2.50

[webservers]
foo.example.com    http_port=80
bar.example.com

# If ansible_ssh_user is not root, ansible_become must be set to true
ansible_become=true

[raleigh]
host2
host3

openshift_examples_modify_imagestreams=true

[southeast:children]
atlanta
raleigh

[Blanktest]

[targets]
localhost              ansible_connection=local
other1.example.com     ansible_connection=ssh        ansible_user=mpdehaan
other2.example.com     ansible_connection=ssh        ansible_user=mdehaan

[atlanta]
host1
host2

[atlanta:vars]
ntp_server=ntp.atlanta.example.com
proxy=proxy.atlanta.example.com
""".strip()


def test_ansible_hosts():
    hosts_info = ansible_hosts.AnsibleHosts(context_wrap(ANSIBLE_HOSTS))

    assert "foo.example.com" in hosts_info["webservers"]
    assert hosts_info["southeast:children"] == ["atlanta", "raleigh"]
    assert hosts_info["targets"]["localhost"]["ansible_connection"] == "local"
    assert hosts_info["atlanta:vars"]["ntp_server"] == "ntp.atlanta.example.com"
    assert hosts_info["global-vars"]["ansible_become"] == "true"
    assert "mail.example.com" in hosts_info["ungrouped-hosts"]
    assert hosts_info["Blanktest"] == {}

    assert hosts_info.has_var("openshift_examples_modify_imagestreams")
    assert hosts_info.has_host("host2")
    assert not hosts_info.has_host("any.example.com")


def test_doc_examples():
    env = {
            'hosts_info': AnsibleHosts(context_wrap(ANSIBLE_HOSTS))
          }
    failed, total = doctest.testmod(ansible_hosts, globs=env)
    assert failed == 0
