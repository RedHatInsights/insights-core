#!/usr/bin/env python
"""
Example Cluster Rule - bash_version
===================================

This rule can be run from the root directory of the insights-core
repo using the following command line::

    $ insights-run -p examples.cluster_rules.bash_version \
            examples/cluster_rules/cluster_hosts.tar.gz

or from the examples/cluster_rules directory::

    $ ./bash_version.py cluster_hosts.tar.gz

"""
from insights import run, make_pass, make_fail
from insights.parsers.installed_rpms import InstalledRpms
from insights.combiners.hostname import hostname
from insights.core.plugins import fact, rule


@fact(InstalledRpms)
def bash_version(rpms):
    """ dict: Returns rpm info for bash on each cluster host """
    rpm = rpms.get_max("bash")
    return {"name": rpm.name, "version": rpm.nvr}


@fact(hostname)
def get_hostname(host):
    """ dict: Returns hostname info for each cluster host """
    return {"hostname": host.fqdn}


@rule(bash_version, get_hostname, cluster=True)
def bash_rule(bash, hostnames):
    """
    Cluster rule to process bash and hostname info

    ``bash`` and ``hostnames`` are Pandas DataFrames for the facts collected
    for each host in the cluster.  See
    https://pandas.pydata.org/pandas-docs/stable/api.html#dataframe
    for information on available attributes and methods.

    Arguments:
        bash (pandas.DataFrame): Includes facts from ``bash_version``
            fact with columns "name" and "version" and one row per
            host in the cluster.
        hostnames (pandas.DataFrame): Includes facts from ``get_hostname``
            fact with column "hostname" and one row per
            host in the cluster.
    """
    if isinstance(bash, dict):
        return make_fail('bash_rule',
                         error_message="Run this rule with a cluster archive")

    return make_pass('bash_rule', bash=bash, hostname=hostnames)


if __name__ == "__main__":
    run(bash_rule, print_summary=True)
