from insights import make_response
from insights.specs import Specs
from insights.core.cluster import ClusterMeta
from insights.core.plugins import fact, rule
from insights.util.fs import sha256

CONTENT = {
    "DISTINCT_NTP_CONFS": "{{confs}} distinct NTP configurations of {{nodes}} members."
}


@fact(Specs.ntp_conf)
def ntp_sha256(ntp):
    return {"sha": sha256(ntp.path)}


@rule(ntp_sha256, ClusterMeta, cluster=True)
def report(shas, meta):
    num_members = meta.num_members
    uniq = shas.sha.unique()
    if len(shas) != num_members or len(uniq) != 1:
        return make_response("DISTINCT_NTP_CONFS", confs=len(uniq), nodes=num_members)


if __name__ == "__main__":
    from insights import run
    run(report, print_summary=True)
