"""
1. The rule import one Condition from upper module ../__init__.py .
2. The imported Condition uses Combiner that depends upon a filterable Parser.
3. The rule does NOT depend upon (import) the filterable Parser directly.
4. The filterable Parser is NOT filtered in the rule as well.
5. The filterable Parser is NOT filtered in the imported Condition as well.

=> Exception is NOT expected
"""

from insights import rule, make_pass
from insights.plugins import os_release_condition


@rule(os_release_condition)
def parser_is_not_used_here_and_upper_init_module(osr):
    return make_pass("FAKE RESULT")
