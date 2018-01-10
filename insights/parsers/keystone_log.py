"""
KeystoneLog - file ``/var/log/keystone/keystone.log``
=====================================================

Module for parsing the log file for Keystone

Typical content of ``keystone.log`` file is::

    2016-11-09 14:31:46.834 818 INFO migrate.versioning.api [-] done
    2016-11-09 14:31:46.834 818 INFO migrate.versioning.api [-] 3 -> 4...
    2016-11-09 14:31:46.872 818 INFO migrate.versioning.api [-] done
    2016-11-09 14:31:48.435 1082 WARNING keystone.assignment.core [-] Deprecated: Use of the identity driver config to automatically configure the same assignment driver has been deprecated, in the "O" release, the assignment driver will need to be expicitly configured if different than the default (SQL).
    2016-11-09 14:31:48.648 1082 WARNING oslo_config.cfg [-] Option "rpc_backend" from group "DEFAULT" is deprecated for removal.  Its value may be silently ignored in the future.
    2016-11-09 14:31:48.680 1082 WARNING oslo_config.cfg [-] Option "rabbit_hosts" from group "oslo_messaging_rabbit" is deprecated for removal.  Its value may be silently ignored in the future.
    2016-11-09 14:31:48.681 1082 WARNING oslo_config.cfg [-] Option "rabbit_userid" from group "oslo_messaging_rabbit" is deprecated for removal.  Its value may be silently ignored in the future.
    2016-11-09 14:31:48.681 1082 WARNING oslo_config.cfg [-] Option "rabbit_password" from group "oslo_messaging_rabbit" is deprecated for removal.  Its value may be silently ignored in the future.
    2016-11-09 14:31:48.774 1082 INFO keystone.cmd.cli [-] Created domain default
    2016-11-09 14:31:48.802 1082 INFO keystone.cmd.cli [req-ace08b7c-d0d2-4b18-b792-1ec3402575b1 - - - - -] Created project admin
    2016-11-09 14:31:48.886 1082 INFO keystone.cmd.cli [req-ace08b7c-d0d2-4b18-b792-1ec3402575b1 - - - - -] Created user admin
    2016-11-09 14:31:48.895 1082 INFO keystone.cmd.cli [req-ace08b7c-d0d2-4b18-b792-1ec3402575b1 - - - - -] Created role admin
    2016-11-09 14:31:48.916 1082 INFO keystone.cmd.cli [req-ace08b7c-d0d2-4b18-b792-1ec3402575b1 - - - - -] Granted admin on admin to user admin.
    2016-11-09 14:31:48.986 1082 INFO keystone.assignment.core [req-ace08b7c-d0d2-4b18-b792-1ec3402575b1 - - - - -] Creating the default role 9fe2ff9ee4384b1894a90878d3e92bab because it does not exist.
    2016-11-09 14:32:09.175 1988 WARNING keystone.assignment.core [-] Deprecated: Use of the identity driver config to automatically configure the same assignment driver has been deprecated, in the "O" release, the assignment driver will need to be expicitly configured if different than the default (SQL).
"""

from .. import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.keystone_log)
class KeystoneLog(LogFileOutput):
    """Class for parsing ``/var/log/keystone/keystone.log`` file.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput`
    """
    pass
