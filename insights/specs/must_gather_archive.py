from insights.core.spec_factory import simple_file
from functools import partial
from insights.core.context import MustGatherContext
from insights.specs import Specs

simple_file = partial(simple_file, context=MustGatherContext)


class MustGatherArchiveSpecs(Specs):

    ceph_health_detail = simple_file("ceph/namespaces/openshift-storage/must_gather_commands/json_output/ceph_health_detail_--format_json-pretty")
