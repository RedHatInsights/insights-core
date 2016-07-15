import unittest

from falafel.mappers import free
from falafel.tests import context_wrap
from falafel.util import keys_in

FREE_TEST = """
Mem:       8060876    2204412    5856464          0      20528     279900
Swap:      7392696      36500    8356196
""".strip()


class TestFree(unittest.TestCase):
    def test_free(self):
        r = free.free(context_wrap(FREE_TEST))
        self.assertTrue(keys_in(["total", "total_swap"], r))
        self.assertEqual(r["total"], 8060876)
        self.assertEqual(r["total_swap"], 7392696)
