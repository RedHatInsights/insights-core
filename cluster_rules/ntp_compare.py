from insights import make_response
from insights.specs import Specs
from insights.core.cluster import ClusterMeta
from insights.core.plugins import cluster_fact, cluster_rule
from insights.util.fs import sha256


@cluster_fact(Specs.ntp_conf)
def ntp_sha256(ntp):
    return {"sha": sha256(ntp.path)}


@cluster_rule(ntp_sha256, ClusterMeta)
def report(shas, meta):
    if len(shas) != meta.num_members or len(shas.sha.unique()) != 1:
        return make_response("DISTINCT_NTP_CONFS")


if __name__ == "__main__":
    from insights import run
    run(report, print_summary=True)
