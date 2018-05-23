from insights.parsers.yum_conf import YumConf
from insights.tests import context_wrap


YUM_CONF = """
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

#  This is the default, if you make this bigger yum won't see if the metadata
# is newer on the remote and so you'll "gain" the bandwidth of not having to
# download the new metadata and "pay" for it by yum not having correct
# information.
#  It is esp. important, to have correct metadata, for distributions like
# Fedora which don't keep old packages around. If you don't like this checking
# interupting your command line usage, it's much better to have something
# manually check the metadata once an hour (yum-updatesd will do this).
# metadata_expire=90m

# PUT YOUR REPOS HERE OR IN separate files named file.repo
# in /etc/yum.repos.d

[rhel-7-server-rhn-tools-beta-debug-rpms]
metadata_expire = 86400
sslclientcert = /etc/pki/entitlement/1234.pem
baseurl = https://cdn.redhat.com/content/beta/rhel/server/7/$basearch/rhn-tools/debug
ui_repoid_vars = basearch
sslverify = 1
name = RHN Tools for Red Hat Enterprise Linux 7 Server Beta (Debug RPMs)
sslclientkey = /etc/pki/entitlement/1234-key.pem
gpgkey = file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-beta,file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release
enabled = 0
sslcacert = /etc/rhsm/ca/redhat-uep.pem
gpgcheck = 1

[bad-repo]
gpgkey =
"""


CONF_PATH = '/etc/yum.conf'


def test_get_yum_conf():
    yum_conf = YumConf(context_wrap(YUM_CONF, path=CONF_PATH))

    assert yum_conf.items('main') == {
        'plugins': '1',
        'keepcache': '0',
        'cachedir': '/var/cache/yum/$basearch/$releasever',
        'exactarch': '1',
        'obsoletes': '1',
        'installonly_limit': '3',
        'debuglevel': '2',
        'gpgcheck': '1',
        'logfile': '/var/log/yum.log'
    }

    assert yum_conf.items('rhel-7-server-rhn-tools-beta-debug-rpms') == {
        u'ui_repoid_vars': u'basearch',
        u'sslverify': u'1',
        u'name': u'RHN Tools for Red Hat Enterprise Linux 7 Server Beta (Debug RPMs)',
        u'sslclientkey': u'/etc/pki/entitlement/1234-key.pem',
        u'enabled': u'0',
        u'gpgkey': [u'file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-beta',
                    u'file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release'],
        u'sslclientcert': u'/etc/pki/entitlement/1234.pem',
        u'baseurl': [u'https://cdn.redhat.com/content/beta/rhel/server/7/$basearch/rhn-tools/debug'],
        u'sslcacert': u'/etc/rhsm/ca/redhat-uep.pem',
        u'gpgcheck': u'1',
        u'metadata_expire': u'86400'
    }

    assert yum_conf.file_name == 'yum.conf'
    assert yum_conf.file_path == '/etc/yum.conf'
