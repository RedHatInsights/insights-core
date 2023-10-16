"""
1. The rule uses one Combiner that depends upon a filterable Parser.
2. The rule does also depend upon (import) the filterable Parser.
3. The filterable Parser is NOT filtered in the rule.

=> Exception is expected
"""
from insights import rule, make_pass
from insights.combiners.os_release import OSRelease
from insights.parsers.dmesg import DmesgLineList


@rule(OSRelease, DmesgLineList)
def parser_is_not_filtered(osr, dmesg):
    return make_pass("FAKE RESULT")
