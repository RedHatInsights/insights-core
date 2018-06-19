import doctest

from insights.parsers import passwd_foreman
from insights.parsers.passwd_foreman import PasswdForeman
from insights.tests import context_wrap


EXAMPLES = """
foreman:x:990:983:Foreman:/usr/share/foreman:/bin/false
"""


def test_passwd_foreman():
    context = PasswdForeman(context_wrap(EXAMPLES))
    assert context.data == ['foreman', 'x', '990', '983', 'Foreman', '/usr/share/foreman', '/bin/false']


def test_systemctl_show_doc_examples():
    env = {
        'passwd_foreman': PasswdForeman(context_wrap(EXAMPLES))
    }
    failed, total = doctest.testmod(passwd_foreman, globs=env)
    assert failed == 0
