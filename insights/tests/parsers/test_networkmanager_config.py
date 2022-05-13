from insights.parsers.networkmanager_config import NetworkManagerConfig
from insights.parsers import networkmanager_config
from insights.tests import context_wrap
import doctest

NETWORKMANAGER_CONF = """
# Configuration file for NetworkManager.
#
# See "man 5 NetworkManager.conf" for details.
#
# The directories /usr/lib/NetworkManager/conf.d/ and /var/run/NetworkManager/conf.d/
# can contain additional configuration snippets installed by packages. These files are
# read before NetworkManager.conf and have thus lowest priority.
# The directory /etc/NetworkManager/conf.d/ can contain additional configuration
# snippets. Those snippets are merged last and overwrite the settings from this main
# file.
#
# The files within one conf.d/ directory are read in asciibetical order.
#
# If /etc/NetworkManager/conf.d/ contains a file with the same name as
# /usr/lib/NetworkManager/conf.d/, the latter file is shadowed and thus ignored.
# Hence, to disable loading a file from /usr/lib/NetworkManager/conf.d/ you can
# put an empty file to /etc with the same name. The same applies with respect
# to the directory /var/run/NetworkManager/conf.d where files in /var/run shadow
# /usr/lib and are themselves shadowed by files under /etc.
#
# If two files define the same key, the one that is read afterwards will overwrite
# the previous one.

[main]
#plugins=ifcfg-rh,ibft
dhcp=dhclient


[logging]
# When debugging NetworkManager, enabling debug logging is of great help.
#
# Logfiles contain no passwords and little sensitive information. But please
# check before posting the file online. You can also personally hand over the
# logfile to a NM developer to treat it confidential. Meet us on #nm on freenode.
# Please post full logfiles except minimal modifications of private data.
#
# You can also change the log-level at runtime via
#   $ nmcli general logging level TRACE domains ALL
# However, usually it's cleaner to enable debug logging
# in the configuration and restart NetworkManager so that
# debug logging is enabled from the start.
#
# You will find the logfiles in syslog, for example via
#   $ journalctl -u NetworkManager
#
# Note that debug logging of NetworkManager can be quite verbose. Some messages
# might be rate-limited by the logging daemon (see RateLimitIntervalSec, RateLimitBurst
# in man journald.conf).
#
#level=TRACE
#domains=ALL
"""

NETWORKMANAGER_CONF_NOTMATCH = """
# Configuration file for NetworkManager.
#
# See "man 5 NetworkManager.conf" for details.
#
# The directories /usr/lib/NetworkManager/conf.d/ and /var/run/NetworkManager/conf.d/
# can contain additional configuration snippets installed by packages. These files are
# read before NetworkManager.conf and have thus lowest priority.
# The directory /etc/NetworkManager/conf.d/ can contain additional configuration
# snippets. Those snippets are merged last and overwrite the settings from this main
# file.
#
# The files within one conf.d/ directory are read in asciibetical order.
#
# If /etc/NetworkManager/conf.d/ contains a file with the same name as
# /usr/lib/NetworkManager/conf.d/, the latter file is shadowed and thus ignored.
# Hence, to disable loading a file from /usr/lib/NetworkManager/conf.d/ you can
# put an empty file to /etc with the same name. The same applies with respect
# to the directory /var/run/NetworkManager/conf.d where files in /var/run shadow
# /usr/lib and are themselves shadowed by files under /etc.
#
# If two files define the same key, the one that is read afterwards will overwrite
# the previous one.

[logging]
# When debugging NetworkManager, enabling debug logging is of great help.
#
# Logfiles contain no passwords and little sensitive information. But please
# check before posting the file online. You can also personally hand over the
# logfile to a NM developer to treat it confidential. Meet us on #nm on freenode.
# Please post full logfiles except minimal modifications of private data.
#
# You can also change the log-level at runtime via
#   $ nmcli general logging level TRACE domains ALL
# However, usually it's cleaner to enable debug logging
# in the configuration and restart NetworkManager so that
# debug logging is enabled from the start.
#
# You will find the logfiles in syslog, for example via
#   $ journalctl -u NetworkManager
#
# Note that debug logging of NetworkManager can be quite verbose. Some messages
# might be rate-limited by the logging daemon (see RateLimitIntervalSec, RateLimitBurst
# in man journald.conf).
#
#level=TRACE
domains=ALL
"""


def test_networkmanager_config_match():
    result = NetworkManagerConfig(context_wrap(NETWORKMANAGER_CONF))
    assert result.get('main', 'dhcp') == 'dhclient'


def test_networkmanager_config_notmatch():
    result = NetworkManagerConfig(context_wrap(NETWORKMANAGER_CONF_NOTMATCH))
    assert result.has_option('main', 'dhcp') is False


def test_networkmanager_config_doc_examples():
    env = {
        'networkmanager_config_obj': NetworkManagerConfig(context_wrap(NETWORKMANAGER_CONF)),
    }
    failed, total = doctest.testmod(networkmanager_config, globs=env)
    assert failed == 0
