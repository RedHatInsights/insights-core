"""
1. The rule uses one Combiner that depends upon a filterable Parser.
2. The rule does also depend upon (import) the filterable Parser directly.
3. The filterable Parser is FILTERED in the rule.

=> Exception is NOT expected
"""
from insights import rule, make_pass
from insights.combiners.os_release import OSRelease
from insights.core.filters import add_filter
from insights.parsers.dmesg import DmesgLineList

add_filter(DmesgLineList, 'Linux version')


@rule(OSRelease, DmesgLineList)
def parser_is_filtered(osr, dmesg):
    return make_pass("FAKE RESULT")
