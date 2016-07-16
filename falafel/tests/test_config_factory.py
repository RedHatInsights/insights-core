import unittest
import sys

import falafel.config.factory as cf
import falafel.config.static as scf
import falafel.config.db as dbcf

from falafel.config import SimpleFileSpec, CommandSpec, PatternSpec

static_specs = {
    "nproc.conf": PatternSpec(r"etc/security/limits\.d/.*-nproc\.conf"),
    "blkid": CommandSpec("/usr/sbin/blkid -c /dev/null"),
    "bond": PatternSpec(r"proc/net/bonding/bond.*"),
    "cciss": PatternSpec(r"proc/driver/cciss/cciss.*"),
}

meta_files = {
    "machine-id": SimpleFileSpec("etc/redhat-access-insights/machine-id"),
    "branch_info": SimpleFileSpec("branch_info"),
    "uploader_log": SimpleFileSpec("var/log/redhat-access-insights/redhat-access-insights.log")
}


class TestConfigFactory(unittest.TestCase):

    def test_get_config_factory(self):
        config = cf.get_config()
        sc = scf.get_config()
        db = dbcf.get_config()

        sc.compose(db)

        self.assertEqual(config, sc)

    def test_get_spec_list(self):
        config = cf.get_config()
        specs = config.get_spec_list('cciss')
        self.assertTrue(specs is not None)
        self.assertTrue(len(specs) == 1)

    def test_get_spec_list_not_exists(self):
        config = cf.get_config()
        specs = config.get_spec_list('not_here')
        self.assertTrue(len(specs) == 0)

    def test_get_meta_spec_list(self):
        config = cf.get_config()
        specs = config.get_meta_spec_list('uploader_log')
        self.assertTrue(specs is not None)
        self.assertTrue(len(specs) == 1)

    def test_get_meta_spec_list_not_exists(self):
        config = cf.get_config()
        specs = config.get_meta_spec_list('not_here')
        self.assertTrue(len(specs) == 0)

    def test_get_specs(self):
        config = cf.get_config()
        specs = config.get_specs('cciss')
        self.assertTrue(specs is not None)
        self.assertTrue(len(specs) == 1)

    def test_get_specs_not_exists(self):
        config = cf.get_config()
        specs = config.get_specs('not_here')
        self.assertTrue(len(specs) == 0)


class TestStaticConfigFactory(unittest.TestCase):
    def test_get_config_factory(self):
        config = scf.get_config(module=sys.modules[__name__])
        self.assertEqual(config.get_specs('blkid')[0], static_specs.get('blkid'))


class TestDatabaseConfigFactory(unittest.TestCase):

    def test_get_config_factory(self):
        config = dbcf.get_config()
        self.assertTrue(config is not None)
