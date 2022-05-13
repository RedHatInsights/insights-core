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
    selinux_config = SelinuxConfig(context_wrap(SELINUX_CONFIG)).data
    assert selinux_config["SELINUX"] == 'enforcing'
    assert selinux_config.get("SELINUXTYPE") == 'targeted'
    assert len(selinux_config) == 2
