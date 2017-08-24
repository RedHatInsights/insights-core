from insights.core.plugins import make_response
from insights.tests import InputData, archive_provider, context_wrap
import insights
from insights.plugins import uname_test as rule

ERROR_KEY = 'UNAME_TEST'

UNAME_TEMPLATE = "Linux testhost1 %s #1 SMP Tue Jan 29 11:47:41 EST 2013 x86_64 x86_64 x86_64 GNU/Linux"

NOT_VULNERABLE = [UNAME_TEMPLATE % kernel for kernel in [
    '2.4.32-100.el6.x86_64',
    '2.6.32-430.el6.x86_64',
    '2.6.32-431.11.2.el6.x86_64',
    '2.6.32-431.11.3.el6.x86_64',
    '2.6.32-432.el6.x86_64',
    '2.7.12-200.el6.x86_64',
]]

VULNERABLE = [UNAME_TEMPLATE % kernel for kernel in [
    '2.6.32-431.el6.x86_64',
    '2.6.32-431.10.1.el6.x86_64',
    '2.6.32-431.11.1.el6.x86_64',
]]


@archive_provider(rule.report)
def integration_tests():
    for uname_line in VULNERABLE:
        kernel = insights.parsers.uname.Uname(context_wrap(uname_line)).kernel
        i = InputData()
        i.add('uname', uname_line)
        expected = make_response(ERROR_KEY, kernel=kernel)
        yield i, [expected]

    for uname_line in NOT_VULNERABLE:
        i = InputData()
        i.add('uname', uname_line)
        yield i, [None]
