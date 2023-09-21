from insights import rule, make_pass
from insights.combiners.os_release import OSRelease
from insights.core.filters import add_filter
from insights.parsers.dmesg import DmesgLineList

add_filter(DmesgLineList, 'Another Key for test')


@rule(OSRelease, DmesgLineList)
def combiner_with_filtered_filterable_parser(cp, rc):
    return make_pass("FAKE RESULT")
