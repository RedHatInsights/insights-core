from insights import SkipComponent
from insights.core.plugins import rule


@rule(requires=[])
def report(local, shared):
    raise SkipComponent("Nothing to see here.")
