import doctest

from insights.parsers import autofs_conf
from insights.tests import context_wrap

AUTOFS_CONF = """
#
# Define default options for autofs.
# Heavily edited for brevity by removing most of the useless comments
#
[ autofs ]
#
# timeout - set the default mount timeout in secons. The internal
#	    program default is 10 minutes, but the default installed
#	    configuration overrides this and sets the timeout to 5
#	    minutes to be consistent with earlier autofs releases.
#
timeout = 300
#
# browse_mode - maps are browsable by default.
#
browse_mode = no
#
# mount_nfs_default_protocol - specify the default protocol used by
# 			       mount.nfs(8). Since we can't identify
# 			       the default automatically we need to
# 			       set it in our configuration.
#
#mount_nfs_default_protocol = 3
mount_nfs_default_protocol = 4
#
# Define global options for the amd parser within autofs.
#
[ amd ]
#
# Override the internal default with the same timeout that
# is used by the override in the autofs configuration, sanity
# only change.
#
dismount_interval = 300
#
# map_type = file
#
"""


def test_doc_examples():
    env = {
        'config': autofs_conf.AutoFSConf(context_wrap(AUTOFS_CONF))
    }
    failed, total = doctest.testmod(autofs_conf, globs=env)
    assert failed == 0


def test_standard_autofs_conf():
    cfg = autofs_conf.AutoFSConf(context_wrap(AUTOFS_CONF))

    assert cfg.get(" autofs ", "timeout") == '300'
    assert cfg.get(" autofs ", "browse_mode") == 'no'
    assert cfg.get(" autofs ", "mount_nfs_default_protocol") == '4'
    assert cfg.get(" amd ", "dismount_interval") == '300'

    # Check that things set in comments do not appear
    assert not cfg.has_option(" amd ", "map_type")
    # Check that nonexistent sections do not appear
    assert "nfs" not in cfg
