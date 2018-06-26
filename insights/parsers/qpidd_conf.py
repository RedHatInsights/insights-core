"""
QpiddConfig - file ``/etc/qpid/qpidd.conf``
===========================================
"""
from insights.specs import Specs

from . import split_kv_pairs
from .. import LegacyItemAccess, Parser, get_active_lines, parser


@parser(Specs.qpidd_conf)
class QpiddConf(Parser, LegacyItemAccess):
    """
    Parse the qpidd configuration file.

    Produces a simple dictionary of keys and values from the configuration
    file contents , stored in the ``data`` attribute.  The object also
    functions as a dictionary itself thanks to the
    :py:class:`insights.core.LegacyItemAccess` mixin class.

    Sample configuration file::

        # Configuration file for qpidd. Entries are of the form:
        # name=value
        #
        # (Note: no spaces on either side of '='). Using default settings:
        # "qpidd --help" or "man qpidd" for more details.
        #cluster-mechanism=ANONYMOUS
        log-enable=error+
        log-to-syslog=yes
        auth=no
        require-encryption=yes
        ssl-require-client-authentication=yes
        ssl-port=5672
        ssl-cert-db=/etc/pki/katello/nssdb
        ssl-cert-password-file=/etc/pki/katello/nssdb/nss_db_password-file
        ssl-cert-name=broker

        interface=lo

    Examples:
        >>> qpidd_conf['auth']
        'no'
        >>> 'require-encryption' in qpidd_conf
        True
    """

    def parse_content(self, content):
        self.data = split_kv_pairs(get_active_lines(content))
