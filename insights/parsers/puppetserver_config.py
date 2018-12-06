"""
PuppetserverConfig - file ``/etc/sysconfig/puppetserver``
=========================================================
"""
from insights.specs import Specs
from insights.util import deprecated
from . import split_kv_pairs
from .. import LegacyItemAccess, Parser, get_active_lines, parser


@parser(Specs.puppetserver_config)
class PuppetserverConfig(Parser, LegacyItemAccess):
    """
    .. warning::
        This parser is deprecated, please use
        :py:class:`insights.parsers.sysconfig.PuppetserverSysconfig` instead.

    Parse the puppetserver configuration file.

    Produces a simple dictionary of keys and values from the configuration
    file contents , stored in the ``data`` attribute.  The object also
    functions as a dictionary itself thanks to the
    :py:class:`insights.core.LegacyItemAccess` mixin class.

    Sample configuration file::

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

        BOOTSTRAP_CONFIG="/etc/puppetlabs/puppetserver/services.d/,/opt/puppetlabs/server/apps/puppetserver/config/services.d/"

        SERVICE_STOP_RETRIES=60

        START_TIMEOUT=300

        RELOAD_TIMEOUT=120

    Examples:
        >>> puppetserver_config['START_TIMEOUT']
        '300'
        >>> 'AUTO' in puppetserver_config
        False
    """
    def __init__(self, *args, **kwargs):
        deprecated(PuppetserverConfig, "Import PuppetserverSysconfig from insights.parsers.sysconfig instead")
        super(PuppetserverConfig, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        self.data = split_kv_pairs(get_active_lines(content))
