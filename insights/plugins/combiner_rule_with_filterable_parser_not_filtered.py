from insights import rule, make_pass
from insights.combiners.os_release import OSRelease
from insights.parsers.dmesg import DmesgLineList


@rule(OSRelease, DmesgLineList)
def combiner_with_filterable_parser_but_no_add_filter(osr, dmesg):
    return make_pass("FAKE RESULT")
