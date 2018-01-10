"""
SelinuxConfig - file ``/etc/selinux/config``
============================================
"""
from .. import get_active_lines, Parser, parser, LegacyItemAccess
from . import split_kv_pairs
from insights.specs import Specs


@parser(Specs.selinux_config)
class SelinuxConfig(Parser, LegacyItemAccess):
    """
    Parse the SELinux configuration file.

    Produces a simple dictionary of keys and values from the configuration
    file contents , stored in the ``data`` attribute.  The object also
    functions as a dictionary itself thanks to the
    :py:class:`insights.core.LegacyItemAccess` mixin class.

    Sample configuration file::

        # This file controls the state of SELinux on the system.
        # SELINUX= can take one of these three values:
        #     enforcing - SELinux security policy is enforced.
        #     permissive - SELinux prints warnings instead of enforcing.
        #     disabled - No SELinux policy is loaded.
        SELINUX=enforcing
        # SELINUXTYPE= can take one of these two values:
        #     targeted - Targeted processes are protected,
        #     minimum - Modification of targeted policy. Only selected processes are protected.
        #     mls - Multi Level Security protection.
        SELINUXTYPE=targeted

    Examples:
        >>> conf = shared[SelinuxConfig]
        >>> conf['SELINUX']
        'enforcing'
        >>> 'AUTORELABEL' in conf
        False
    """

    def parse_content(self, content):
        self.data = split_kv_pairs(get_active_lines(content))
