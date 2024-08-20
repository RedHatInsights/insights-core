import doctest
import pytest

from insights.tests import context_wrap
from insights.core.dr import SkipComponent
from insights.parsers import lsattr


LSATTR_OUTPUT1 = """
./grub2-tools-2.02-0.86.el7.x86_64.rpm
""".strip()

LSATTR_OUTPUT2 = """
---------------- ./grub2-tools-2.02-0.86.el7.x86_64.rpm

------i--------- ./grub2-common-2.02-0.86.el7.noarch.rpm
---------------- ./grub2-tools-minimal-2.02-0.86.el7.x86_64.rpm
lsattr: No such file or directory while trying to stat a/f
"""

LSATTR_OUTPUT3 = """


"""

LSATTR_OUTPUT4 = """
lsattr: No such file or directory while trying to stat a/f
"""

LSATTR_OUTPUT5 = """
---------------- ./grub2-tools-2.02-0.86.el7.x86_64.rpm
------i--------- ./grub2-common-2.02-0.86.el7.noarch.rpm
---------------- ./grub2-tools-minimal-2.02-0.86.el7.x86_64.rpm
"""


def test_doc():
    failed_count, _ = doctest.testmod(
        lsattr,
        globs={'lsattr_obj': lsattr.LsAttr(context_wrap(LSATTR_OUTPUT2))}
    )
    assert failed_count == 0


def test_except():
    with pytest.raises(SkipComponent):
        lsattr.LsAttr(context_wrap(LSATTR_OUTPUT1))
    with pytest.raises(SkipComponent):
        lsattr.LsAttr(context_wrap(LSATTR_OUTPUT3))


def test_normal_output():
    attr_obj = lsattr.LsAttr(context_wrap(LSATTR_OUTPUT2))
    assert len(attr_obj) == 4
    assert attr_obj['./grub2-tools-2.02-0.86.el7.x86_64.rpm'] == ''
    assert attr_obj['./grub2-common-2.02-0.86.el7.noarch.rpm'] == 'i'
    assert attr_obj['./grub2-tools-minimal-2.02-0.86.el7.x86_64.rpm'] == ''
    assert 'non-exist' in attr_obj
    assert len(attr_obj['non-exist']) == 1
    assert attr_obj['non-exist'][0] == 'lsattr: No such file or directory while trying to stat a/f'

    attr_obj2 = lsattr.LsAttr(context_wrap(LSATTR_OUTPUT4))
    assert 'non-exist' in attr_obj2
    assert len(attr_obj2) == 1
    assert len(attr_obj2['non-exist']) == 1
    assert attr_obj2['non-exist'][0] == 'lsattr: No such file or directory while trying to stat a/f'

    attr_obj3 = lsattr.LsAttr(context_wrap(LSATTR_OUTPUT5))
    assert 'non-exist' not in attr_obj3
