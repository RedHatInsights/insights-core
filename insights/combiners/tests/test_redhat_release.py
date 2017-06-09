import unittest
from insights.parsers.uname import Uname
from insights.parsers.redhat_release import RedhatRelease
from insights.combiners.redhat_release import redhat_release
from insights.tests import context_wrap

UNAME = "Linux localhost.localdomain 3.10.0-327.rt56.204.el7.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"
BAD_UNAME = "Linux localhost.localdomain 2.6.24.7-101.el5rt.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"

REDHAT_RELEASE = """
Red Hat Enterprise Linux Server release 7.2 (Maipo)
""".strip()

FEDORA = """
Fedora release 23 (Twenty Three)
""".strip()


class TestRedhatRelease(unittest.TestCase):
    def test_uname(self):
        un = Uname(context_wrap(UNAME))
        shared = {Uname: un}
        expected = (7, 2)
        result = redhat_release(None, shared)
        self.assertEqual(result.major, expected[0])
        self.assertEqual(result.minor, expected[1])

    def test_redhat_release(self):
        rel = RedhatRelease(context_wrap(REDHAT_RELEASE))
        shared = {RedhatRelease: rel}
        expected = (7, 2)
        result = redhat_release(None, shared)
        self.assertEqual(result.major, expected[0])
        self.assertEqual(result.minor, expected[1])

    def test_both(self):
        un = Uname(context_wrap(UNAME))
        rel = RedhatRelease(context_wrap(REDHAT_RELEASE))
        shared = {Uname: un, RedhatRelease: rel}
        expected = (7, 2)
        result = redhat_release(None, shared)
        self.assertEqual(result.major, expected[0])
        self.assertEqual(result.minor, expected[1])

    def test_raise(self):
        un = Uname(context_wrap(BAD_UNAME))
        shared = {Uname: un}
        with self.assertRaises(Exception):
            redhat_release(None, shared)
