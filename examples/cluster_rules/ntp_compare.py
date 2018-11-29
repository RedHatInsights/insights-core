#!/usr/bin/env python
"""
Example Cluster Rule - ntp_compare
==================================
This rule can be run from the root directory of the insights-core
repo using the following command line::

    $ insights-run -p examples.cluster_rules.ntp_compare \
            -i topology_example \
            examples/cluster_rules/cluster_hosts.tar.gz

or from the examples/cluster_rules directory::

    $ ./ntp_compare.py -i topology_example cluster_hosts.tar.gz

"""
from insights import make_fail, make_pass
from insights.specs import Specs
from insights.core.cluster import ClusterMeta
from insights.core.plugins import fact, rule
from insights.util.fs import sha256

# Jinja template to use for make_pass
SUCCESS_TEMPLATE = """
Servers:
{% for n in servers %}
    {{ n }}
{% endfor %}

Nodes:
{% for n in nodes %}
    {{ n }}
{% endfor %}""".strip()

# The CONTENT variable provides the Jinja content templates that will
# be displayed depending upon which code is returned by make_pass/make_fail
CONTENT = {
    "DISTINCT_NTP_CONFS": "{{confs}} distinct NTP configurations of {{nodes}} members.",
    "MATCHING_NTP_CONFS": SUCCESS_TEMPLATE
}


@fact(Specs.ntp_conf)
def ntp_sha256(ntp):
    """ datasource object: Datasource for the ntp.conf spec """
    return {"sha": sha256(ntp.path)}


@rule(ntp_sha256, ClusterMeta, cluster=True)
def report(shas, meta):
    """
    Cluster rule to compare ntp.conf files across a cluster

    ``shas`` is a Pandas DataFrame for the facts for each host
    by the fact ``ntp_sha256``.  See
    https://pandas.pydata.org/pandas-docs/stable/api.html#dataframe
    for information on available attributes and methods.

    ``meta`` is a dictionary that contains the information from the
    cluster topology file provided by the ``-i`` switch.  The dictionary
    keys are the sections, and the values are a list of the host
    information provided in the toplolgy file.

    Arguments:
        shas (pandas.DataFrame): Includes facts from ``ntp_sha256``
            fact with column "sha" and one row per host in the cluster.
        meta (dict): Keys are the sections in the topology file and
            values are a list of the values in the section.
    """
    num_members = meta.num_members
    uniq = shas.sha.unique()
    if len(shas) != num_members or len(uniq) != 1:
        return make_fail("DISTINCT_NTP_CONFS", confs=len(uniq), nodes=num_members)

    return make_pass("MATCHING_NTP_CONFS", nodes=meta['nodes'], servers=meta['servers'])


if __name__ == "__main__":
    from insights import run
    run(report, print_summary=True)
