# Cluster Rules Examples

The examples in this directory demonstrate how to create rules for
*cluster archives*.  A cluster archive contains multiple archives and optional
metadata.  Each archive in the cluster archive represents a single system in
the cluster.  Cluster rules can be written that can evaluate one or more
systems in the cluster.

The cluster can be defined using an optional *topology* file that is in the
format of an Ansible hosts file.  This format is similar to an INI type file,
see the [Ansible hosts file documentation][1] for more detailed information.

## Contents of this Directory

* [allnodes_cpu.py](./allnodes_cpu.py) - Example cluster rules that use
  a topology file and includes a custom spec and parser.
* [bash_version.py](./bash_version.py) - Example cluster rules that don't
  use a topology file.
* [cluster_hosts.tar.gz](./cluster_hosts.tar.gz) - Example cluster archive
  containing four host archives.
* [\_\_init\_\_.py](./\_\_init\_\_.py) - Make this directory a package that can
  be access using the Python syntax `examples.cluster_rules`.
* [ntp_compare.py](./ntp_compare.py) - Example cluster rule that uses
  a topology file and formated content.
* [topology_example](./topology_example) - Sample cluster topology file in
  Ansible host file format.

[1]: https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html#hosts-and-groups
