import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import rear_conf
from insights.parsers.rear_conf import RearLocalConf
from insights.tests import context_wrap

RDMA_CONFIG = """
# This file etc/rear/local.conf is intended for the user's
# manual configuration of Relax-and-Recover (ReaR).
# For configuration through packages and other automated means
# we recommend a separated file named site.conf next to this file
# and leave local.conf as is (ReaR upstream will never ship a site.conf).
# The default OUTPUT=ISO creates the ReaR rescue medium as ISO image.
# You need to specify your particular backup and restore method for your data
# as the default BACKUP=REQUESTRESTORE does not really do that (see "man rear").
# Configuration variables are documented in /usr/share/rear/conf/default.conf
# and the examples in /usr/share/rear/conf/examples/ can be used as templates.
# ReaR reads the configuration files via the bash builtin command 'source'
# so bash syntax like VARIABLE="value" (no spaces at '=') is mandatory.
# Because 'source' executes the content as bash scripts you can run commands
# within your configuration files, in particular commands to set different
# configuration values depending on certain conditions as you need like
# CONDITION_COMMAND && VARIABLE="special_value" || VARIABLE="usual_value"
# but that means CONDITION_COMMAND gets always executed when 'rear' is run
# so ensure nothing can go wrong if you run commands in configuration files.
BACKUP_RESTORE_MOVE_AWAY_FILES=( /boot/grub/grubenv /boot/grub2/grubenv )
""".strip()

REAR_CONF_EMPTY = """
""".strip()


def test_rdma_config():
    local_conf = RearLocalConf(context_wrap(RDMA_CONFIG))
    assert len(local_conf.lines) == 1
    assert local_conf.lines[0] == "BACKUP_RESTORE_MOVE_AWAY_FILES=( /boot/grub/grubenv /boot/grub2/grubenv )"


def test_rdma_config_empty():
    with pytest.raises(SkipComponent):
        RearLocalConf(context_wrap(REAR_CONF_EMPTY))


def test_rdma_config_doc():
    env = {
            'local_conf': RearLocalConf(context_wrap(RDMA_CONFIG)),
          }
    failed, total = doctest.testmod(rear_conf, globs=env)
    assert failed == 0
