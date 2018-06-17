#!/usr/bin/env python
from insights import run
from insights.parsers.installed_rpms import InstalledRpms
from insights.combiners.hostname import hostname
from insights.core.plugins import fact, rule


@fact(InstalledRpms)
def bash_version(rpms):
    rpm = rpms.get_max("bash")
    return {"name": rpm.name, "version": rpm.nvr}


@fact(hostname)
def get_hostname(hn):
    return {"hostname": hn.fqdn}


@rule(bash_version, get_hostname, cluster=True)
def bash_rule(bash, hn):
    pass


if __name__ == "__main__":
    run(bash_version, print_summary=True)
