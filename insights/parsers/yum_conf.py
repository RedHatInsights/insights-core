"""
YumConf - file ``/etc/yum.conf``
================================

This module provides parsing for the ``/etc/yum.conf`` file.
The ``YumConf`` class parses the information in the file
``/etc/yum.conf``. See the ``IniConfigFile`` class for more
information on attributes and methods.

Sample input data looks like::

    [main]

    cachedir=/var/cache/yum/$basearch/$releasever
    keepcache=0
    debuglevel=2
    logfile=/var/log/yum.log
    exactarch=1
    obsoletes=1
    gpgcheck=1
    plugins=1
    installonly_limit=3

    [rhel-7-server-rpms]

    metadata_expire = 86400
    baseurl = https://cdn.redhat.com/content/rhel/server/7/$basearch
    name = Red Hat Enterprise Linux 7 Server (RPMs)
    gpgkey = file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release
    enabled = 1
    gpgcheck = 1

Examples:

    >>> yconf = shared[YumConf]
    >>> yconf.defaults()
    {'admin_token': 'ADMIN', 'compute_port': '8774'}
    >>> 'main' in yconf
    True
    >>> 'rhel-7-server-rpms' in yconf
    True
    >>> yconf.has_option('main', 'gpgcheck')
    True
    >>> yconf.has_option('main', 'foo')
    False
    >>> yconf.get('rhel-7-server-rpms', 'enabled')
    '1'
    >>> yconf.items('main')
    {'plugins': '1',
     'keepcache': '0',
     'cachedir': '/var/cache/yum/$basearch/$releasever',
     'exactarch': '1',
     'obsoletes': '1',
     'installonly_limit': '3',
     'debuglevel': '2',
     'gpgcheck': '1',
     'logfile': '/var/log/yum.log'}
"""

import six
from insights.contrib.ConfigParser import NoOptionError
from .. import parser, IniConfigFile
from insights.specs import Specs


@parser(Specs.yum_conf)
class YumConf(IniConfigFile):
    """Parse contents of file ``/etc/yum.conf``."""
    def parse_content(self, content):
        super(YumConf, self).parse_content(content)
        # File /etc/yum.conf may contain repos definitions.
        # Keywords 'gpgkey' and 'baseurl' might contain multiple
        # values separated by comma. Convert those values into a list.
        for section in self.sections():
            for key in ('gpgkey', 'baseurl'):
                try:
                    value = self.get(section, key)
                    if value and isinstance(value, six.string_types):
                        self.data.set(section, key, value.split(','))
                except NoOptionError:
                    pass
