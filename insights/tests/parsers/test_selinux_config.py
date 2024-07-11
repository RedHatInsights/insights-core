import doctest

from insights.parsers import selinux_config
from insights.parsers.selinux_config import SelinuxConfig
from insights.tests import context_wrap

SELINUX_CONFIG = """
# This file controls the state of SELinux on the system.
# SELINUX= can take one of these three values:
#     enforcing - SELinux security policy is enforced.
#     permissive - SELinux prints warnings instead of enforcing.
#     disabled - No SELinux policy is loaded.
SELINUX=enforcing

 # SELINUXTYPE= can take one of three two values:
 #     targeted - Targeted processes are protected,
 #     minimum - Modification of targeted policy. Only selected processes are protected.
 #     mls - Multi Level Security protection.
SELINUXTYPE=targeted

"""


def test_selinux_config():
    selinux_conf = SelinuxConfig(context_wrap(SELINUX_CONFIG))
    assert selinux_conf["SELINUX"] == 'enforcing'
    assert selinux_conf.get("SELINUXTYPE") == 'targeted'
    assert len(selinux_conf) == 2


def test_doc_examples():
    env = {
            'conf': SelinuxConfig(context_wrap(SELINUX_CONFIG))
          }
    failed, total = doctest.testmod(selinux_config, globs=env)
    assert failed == 0
