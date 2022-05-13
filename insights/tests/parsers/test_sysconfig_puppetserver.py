from insights.parsers.sysconfig import PuppetserverSysconfig
from insights.tests import context_wrap

PUPPETSERVER_CONFIG = """
###########################################
# Init settings for puppetserver
###########################################

# Location of your Java binary (version 7 or higher)
JAVA_BIN="/usr/bin/java"

# Modify this if you'd like to change the memory allocation, enable JMX, etc
JAVA_ARGS="-Xms2g -Xmx2g -XX:MaxPermSize=256m"

# These normally shouldn't need to be edited if using OS packages
USER="puppet"
GROUP="puppet"
INSTALL_DIR="/opt/puppetlabs/server/apps/puppetserver"
CONFIG="/etc/puppetlabs/puppetserver/conf.d"

# Bootstrap path
BOOTSTRAP_CONFIG="/etc/puppetlabs/puppetserver/services.d/,/opt/puppetlabs/server/apps/puppetserver/config/services.d/"

# SERVICE_STOP_RETRIES can be set here to alter the default stop timeout in
# seconds.  For systemd, the shorter of this setting or 'TimeoutStopSec' in
# the systemd.service definition will effectively be the timeout which is used.
SERVICE_STOP_RETRIES=60

# START_TIMEOUT can be set here to alter the default startup timeout in
# seconds.  For systemd, the shorter of this setting or 'TimeoutStartSec'
# in the service's systemd.service configuration file will effectively be the
# timeout which is used.
START_TIMEOUT=300


# Maximum number of seconds that can expire for a service reload attempt before
# the result of the attempt is interpreted as a failure.
RELOAD_TIMEOUT=120
"""


def test_puppetserver_config():
    puppetserver_config = PuppetserverSysconfig(context_wrap(PUPPETSERVER_CONFIG))
    assert puppetserver_config["GROUP"] == 'puppet'
    assert puppetserver_config.get("START_TIMEOUT") == '300'
    assert len(puppetserver_config.keys()) == 10
