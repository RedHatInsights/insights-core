from insights.parsers.uname import Uname
from insights.core.plugins import make_response
from insights.tests import archive_provider, context_wrap, InputData

from insights.core.fava import load_fava_plugin
fava_vulnerable_kernel = load_fava_plugin('insights.plugins.fava_vulnerable_kernel')

ERROR_KEY = 'FAVA_VULNERABLE_KERNEL'

UNAME_TEMPLATE = "Linux testhost1 %s #1 SMP Tue Jan 29 11:47:41 EST 2013 x86_64 x86_64 x86_64 GNU/Linux"

NOT_VULNERABLE = [
    '2.4.32-100.el6.x86_64',
    '2.6.32-430.el6.x86_64',
    '2.6.32-431.11.2.el6.x86_64',
    '2.6.32-431.11.3.el6.x86_64',
    '2.6.32-432.el6.x86_64',
    '2.7.12-200.el6.x86_64',
]


VULNERABLE = [
    '2.6.32-431.el6.x86_64',
    '2.6.32-431.10.1.el6.x86_64',
    '2.6.32-431.11.1.el6.x86_64',
]


def test_vulnerable_kernel():
    for kernel in NOT_VULNERABLE:
        uname_line = UNAME_TEMPLATE % kernel
        result = fava_vulnerable_kernel.report({Uname: Uname(context_wrap(uname_line))})
        expected = None
        if not (result == expected):
            print result
            print expected
            assert result == expected
            assert False
    for kernel in VULNERABLE:
        uname_line = UNAME_TEMPLATE % kernel
        result = fava_vulnerable_kernel.report({Uname: Uname(context_wrap(uname_line))})
        expected = make_response(ERROR_KEY, kernel=kernel)
        if not (result == expected):
            print result
            print expected
            assert result == expected
            assert False


@archive_provider(fava_vulnerable_kernel.report)
def integration_tests():
    for kernel in VULNERABLE:
        uname_line = UNAME_TEMPLATE % kernel
        i = InputData()
        i.add('uname', uname_line)
        expected = make_response(ERROR_KEY, kernel=kernel)
        yield i, [expected]

    for kernel in NOT_VULNERABLE:
        uname_line = UNAME_TEMPLATE % kernel
        i = InputData()
        i.add('uname', uname_line)
        yield i, [None]
