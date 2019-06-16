#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
