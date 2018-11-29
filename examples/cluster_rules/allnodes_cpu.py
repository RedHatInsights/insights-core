#!/usr/bin/env python
"""
Example Cluster Rule - allnodes_cpu
===================================

This example demonstrates a custome spec, parser, facts, combiner
and multiple cluster rules.  It can be run using the command::

    $ insights-run -p examples.cluster_rules.allnodes_cpu \
            -i topology_allnodes \
            examples/cluster_rules/cluster_hosts.tar.gz

or from the examples/cluster_rules directory::

    $ ./allnodes_cpu.py -i topology_allnodes \
            examples/cluster_rules/cluster_hosts.tar.gz
"""
from __future__ import print_function
from colorama import Fore, Style  # noqa: F401
from insights import make_response
from insights.core import YAMLParser
from insights.core.cluster import ClusterMeta
from insights.core.plugins import combiner, fact, parser, rule
from insights.core.spec_factory import SpecSet, simple_file
from insights.parsers.cpuinfo import CpuInfo

PODS_PER_CORE = 10
MAX_PODS = 250
MASTER_MIN_CORE = 4


# Define a datasource for node-config.yaml since core doesn't ship with one
class Specs(SpecSet):
    """ Specs to collect data the cluster hosts """
    node_config_yaml = simple_file("etc/origin/node/node-config.yaml")


# Parse the yaml
@parser(Specs.node_config_yaml)
class NodeConfig(YAMLParser):
    """
    Parser to parse the contents of the node_config_yaml spec

    Implementation is provided by the YAMLParser class.
    """
    pass


# A fact is generated from every node in the cluster
# Return from it a dictionary or list of dictionaries. You'll access these
# later
@fact(CpuInfo, NodeConfig)
def cluster_info(cpu, cfg):
    """
    Collects fact for each host

    Collects the cpu and node configuration facts to be used by the rule.

    Arguments:
        cpu (CpuInfo): Parser object for the cpu info.
        cfg (NodeConfig): Parser object for the node configuration.

    Returns:
        dict: Dictionary of fact information including the keys
        ``cpu_count``, ``pods_per_core_int``, ``pods_per_core_customized``,
        ``max_pods``, and ``max_pods_customized``.
    """
    cpus = cpu.cpu_count
    pods_per_core = cfg.doc.find("pods-per-core")
    pods_per_core_int = int(pods_per_core.value) if pods_per_core else PODS_PER_CORE
    cfg_max_pods = cfg.doc.find("max-pods")
    cfg_max_pods_int = int(cfg_max_pods.value) if cfg_max_pods else MAX_PODS
    calc_max_pods = cpus * pods_per_core_int

    return {
        "cpu_count": cpus,
        "pods_per_core": pods_per_core_int,
        "pods_per_core_customized": bool(pods_per_core),
        "max_pods": min(cfg_max_pods_int, calc_max_pods),
        "max_pods_customized": bool(cfg_max_pods)
    }


def master_etcd(info, meta, max_pod_cluster, label):
    """ Function used to create the response for all master node types """
    nodes = meta.get(label, []) or []
    info = info[info["machine_id"].isin(nodes)]
    if info.empty:
        return

    cpu_factor = max_pod_cluster / 1000.0
    nocpu_expected = MASTER_MIN_CORE + (max_pod_cluster / 1000.0)
    bad = info[info["cpu_count"] < nocpu_expected]
    good = info[info["cpu_count"] >= nocpu_expected]
    return make_response("MASTER_ETCD",
                         nocpu_expected=nocpu_expected, cpu_factor=cpu_factor,
                         bad=bad, good=good, max_pod_cluster=max_pod_cluster,
                         GREEN=Fore.GREEN, RED=Fore.RED, YELLOW=Fore.YELLOW, NC=Style.RESET_ALL)


def infra_nodes(info, meta, max_pod_cluster, label, key):
    """ Function used to create the response for all infra node types """
    nodes = meta.get(label, []) or []
    infos = info[info["machine_id"].isin(nodes)]
    if infos.empty:
        return
    return make_response(key, max_pod_cluster=max_pod_cluster, infos=infos,
                         GREEN=Fore.GREEN, RED=Fore.RED, YELLOW=Fore.YELLOW, NC=Style.RESET_ALL)


@combiner(cluster_info, cluster=True)
def calc_max_pos_cluster(info):
    """
    Combiner summarizes cluster info after cluster_info facts
    have been collected for all cluster hosts.global
    """
    return info["max_pods"].sum()


@rule(cluster_info, calc_max_pos_cluster, ClusterMeta, cluster=True)
def report_master(info, max_pod_cluster, meta):
    """ Rule to report for master node types """
    return master_etcd(info, meta, max_pod_cluster, "master")


@rule(cluster_info, calc_max_pos_cluster, ClusterMeta, cluster=True)
def report_etcd(info, max_pod_cluster, meta):
    """ Rule to report for etcd node types """
    return master_etcd(info, meta, max_pod_cluster, "etcd")


@rule(cluster_info, calc_max_pos_cluster, ClusterMeta, cluster=True)
def report_infra(info, max_pod_cluster, meta):
    """ Rule to report for infra node types """
    return infra_nodes(info, meta, max_pod_cluster, "infra", "INFRA")


@rule(cluster_info, calc_max_pos_cluster, ClusterMeta, cluster=True)
def report_nodes(info, max_pod_cluster, meta):
    """ Rule to report for nodes node types """
    return infra_nodes(info, meta, max_pod_cluster, "nodes", "NODES")


#
# Jinga templates for all output
#
MASTER_CONTENT = """
{% for idx, row in good.iterrows() -%}
{{row.machine_id}}: {{GREEN}}[passed]{{NC}}
{% endfor %}
{% for idx, row in bad.iterrows() -%}
{{row.machine_id}}: {{RED}}[failed]{{NC}} - reason: {{row.cpu_count}} is less than the expected {{nocpu_expected}} cores
{% endfor %}
""".strip()

NODE_CONTENT = """
{% for idx, row in infos.iterrows() %}
{{row.machine_id}}:
CPUS: {{row.cpu_count}}
{%- if row.pods_per_core_customized -%} {{YELLOW}} pods-per-core customized: {{row.pods_per_core}}{{NC}} {% endif %}
{%- if row.max_pods_customized -%} {{YELLOW}} max-pods customized: {{row.max_pods}}{{NC}} {% endif %}
max pods: {{row.max_pods}}
{% endfor %}
""".strip()

CONTENT = {
    "MASTER_ETCD": MASTER_CONTENT,
    "INFRA": NODE_CONTENT,
    "NODES": NODE_CONTENT + """
================================
max app pods cluster: {{max_pod_cluster}}
""".strip()
}

if __name__ == "__main__":
    from insights import run
    run([report_master, report_etcd, report_infra, report_nodes], print_summary=True)
