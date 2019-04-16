from __future__ import print_function
from insights.parsers.uname import Uname
from insights.core.plugins import make_fail
from insights.tests import context_wrap, InputData, run_test
from insights.specs import Specs

from insights.plugins import vulnerable_kernel

ERROR_KEY = 'VULNERABLE_KERNEL'

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
        result = vulnerable_kernel.report(Uname(context_wrap(uname_line)))
        expected = None
        if not (result == expected):
            print(result)
            print(expected)
            assert result == expected
            assert False
    for kernel in VULNERABLE:
        uname_line = UNAME_TEMPLATE % kernel
        result = vulnerable_kernel.report(Uname(context_wrap(uname_line)))
        expected = make_fail(ERROR_KEY, kernel=kernel)
        if not (result == expected):
            print(result)
            print(expected)
            assert result == expected
            assert False


def generate_inputs(things):
    for kernel in things:
        uname_line = UNAME_TEMPLATE % kernel
        i = InputData()
        i.add(Specs.uname, uname_line)
        yield (kernel, i)


def test_vulnerable_kernel_integration():
    comp = vulnerable_kernel.report
    for kernel, i in generate_inputs(VULNERABLE):
        expected = make_fail(ERROR_KEY, kernel=kernel)
        run_test(comp, i, expected)

    for _, i in generate_inputs(NOT_VULNERABLE):
        run_test(comp, i, None)
