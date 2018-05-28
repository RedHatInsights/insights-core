#!/usr/bin/env python
from insights import run
from insights.parsers.installed_rpms import InstalledRpms
from insights.combiners.hostname import hostname
from insights.core.plugins import fact, cluster_rule


@fact(InstalledRpms)
def bash_version(rpms):
    rpm = rpms.get_max("bash")
    return {"name": rpm.name, "version": rpm.nvr}


# bet there'll be a bunch of these
@fact(hostname)
def get_hostname(hn):
    return {"hostname": hn.fqdn}


@cluster_rule(bash_version, get_hostname)
def bash_rule(bash, hn):
    print(bash)
    print(hn)


if __name__ == "__main__":
    run(bash_version, print_summary=True)
