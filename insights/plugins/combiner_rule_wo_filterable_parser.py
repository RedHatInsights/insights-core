from insights import rule, make_pass
from insights.combiners.os_release import OSRelease


@rule(OSRelease)
def combiner_wo_filterable_parser(cp):
    return make_pass("FAKE RESULT")
