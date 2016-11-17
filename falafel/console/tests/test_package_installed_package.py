import unittest
from pkg_resources import Distribution
from pkg_resources import get_distribution
from falafel.console.package import MetaPattern
from falafel.console.package import InstalledPackage

NAME = "falafel"


class TestInstalledPackage(unittest.TestCase):

    def setUp(self):
        this_package = get_distribution(NAME)
        self.pkg = InstalledPackage(this_package)

    def test___init__(self):
        self.assertIsInstance(self.pkg.dist, Distribution)

    def test_has_metapair(self):
        mp = MetaPattern('Name', NAME)
        has_metapair = self.pkg.has_metapair(mp)
        self.assertTrue(has_metapair)

    def test_has_metapair_neg(self):
        mp = MetaPattern('Name', '{}_neg'.format(NAME))
        has_metapair = self.pkg.has_metapair(mp)
        self.assertFalse(has_metapair)

    def test_list_modules(self):
        modules = self.pkg.list_modules()
        self.assertIn(NAME, modules)
        self.assertIn('{}.console'.format(NAME), modules)
        self.assertNotIn('{}.console.tests'.format(NAME), modules)

    def test_all(self):
        packages = InstalledPackage.all()

        _pkgs = [pkg for pkg in packages if pkg.dist.project_name == NAME]
        self.assertEqual(len(_pkgs), 1)

    def test_by_metadata(self):
        packages = InstalledPackage.by_metadata('Name', NAME)
        self.assertEqual(len(packages), 1)
