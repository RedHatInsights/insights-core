"""
1. The rule uses one Combiner that depends upon a filterable Parser.
2. The rule does NOT depend upon (import) the filterable Parser directly.
3. The filterable Parser is NOT filtered in the rule as well.

=> Exception is NOT expected
"""
from insights import rule, make_pass
from insights.combiners.os_release import OSRelease


@rule(OSRelease)
def parser_is_not_used(osr):
    return make_pass("FAKE RESULT")
