import sys

import insights.config.factory as cf
import insights.config.static as scf
import insights.config.db as dbcf

from insights.config import SimpleFileSpec, CommandSpec, PatternSpec

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

openshift = {}


def test_get_config_factory():
    config = cf.get_config()
    sc = scf.get_config()
    db = dbcf.get_config()

    sc.compose(db)

    assert config == sc


def test_get_spec_list():
    config = cf.get_config()
    specs = config.get_spec_list('cciss')
    assert specs is not None
    assert len(specs) == 1


def test_get_spec_list_not_exists():
    config = cf.get_config()
    specs = config.get_spec_list('not_here')
    assert len(specs) == 0


def test_get_meta_spec_list():
    config = cf.get_config()
    specs = config.get_meta_spec_list('uploader_log')
    assert specs is not None
    assert len(specs) == 1


def test_get_meta_spec_list_not_exists():
    config = cf.get_config()
    specs = config.get_meta_spec_list('not_here')
    assert len(specs) == 0


def test_get_specs():
    config = cf.get_config()
    specs = config.get_specs('cciss')
    assert specs is not None
    assert len(specs) == 1


def test_get_specs_not_exists():
    config = cf.get_config()
    specs = config.get_specs('not_here')
    assert len(specs) == 0


def test_get_static_config_factory():
    config = scf.get_config(module=sys.modules[__name__])
    assert config.get_specs('blkid')[0] == static_specs.get('blkid')


def test_get_db_config_factory():
    config = dbcf.get_config()
    assert config is not None
