from insights.core.plugins import make_response, rule
from insights.parsers.uname import Uname


@rule(requires=[Uname])
def report(broker):
    if broker[Uname].fixed_by('2.6.32-431.11.2.el6', introduced_in='2.6.32-431.el6'):
        return make_response("VULNERABLE_KERNEL", kernel=broker[Uname].kernel)
