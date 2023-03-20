from insights.tests import context_wrap
from insights.parsers.x86_debug import X86PTIEnabled, X86IBPBEnabled, X86IBRSEnabled, X86RETPEnabled
from insights.combiners import x86_page_branch
from insights.combiners.x86_page_branch import X86PageBranch
import doctest


def test_values():
    for val in ['0', '1', '2']:
        ptienabled = X86PTIEnabled(context_wrap(val))
        ibpbenabled = X86IBPBEnabled(context_wrap(val))
        ibrsenabled = X86IBRSEnabled(context_wrap(val))
        res = X86PageBranch(ptienabled, ibpbenabled, ibrsenabled, None)
        assert res.pti == int(val)
        assert res.ibpb == int(val)
        assert res.ibrs == int(val)
        assert res.retp is None

    for val in ['0', '1', '2']:
        ptienabled = X86PTIEnabled(context_wrap(val))
        ibpbenabled = X86IBPBEnabled(context_wrap(val))
        ibrsenabled = X86IBRSEnabled(context_wrap(val))
        retpenabled = X86RETPEnabled(context_wrap(val))
        res = X86PageBranch(ptienabled, ibpbenabled, ibrsenabled, retpenabled)
        assert res.pti == int(val)
        assert res.ibpb == int(val)
        assert res.ibrs == int(val)
        assert res.retp == int(val)


def test_x86_enabled_documentation():
    """
    Here we test the examples in the documentation automatically using
    doctest.  We set up an environment which is similar to what a rule
    writer might see - a '/sys/kernel/debug/x86/*_enabled' output
    that has been passed in as a parameter to the rule declaration.
    """
    env = {
            'dv': X86PageBranch(X86PTIEnabled(context_wrap('1')),
                X86IBPBEnabled(context_wrap('3')),
                X86IBRSEnabled(context_wrap('2')),
                X86RETPEnabled(context_wrap('0')))
                }
    failed, total = doctest.testmod(x86_page_branch, globs=env)
    assert failed == 0
