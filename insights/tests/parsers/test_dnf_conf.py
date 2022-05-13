import doctest

from insights.tests import context_wrap
from insights.parsers import dnf_conf
from insights.parsers.dnf_conf import DnfConf


DNF_CONF = """
[main]
gpgcheck=1
installonly_limit=3
clean_requirements_on_remove=True
best=False
skip_if_unavailable=True

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


CONF_PATH = '/etc/dnf/dnf.conf'


def test_doc_examples():
    env = {
        'dconf': DnfConf(context_wrap(DNF_CONF, path=CONF_PATH)),
    }
    failed, total = doctest.testmod(dnf_conf, globs=env)
    assert failed == 0


def test_get_dnf_conf():
    dnf_conf = DnfConf(context_wrap(DNF_CONF, path=CONF_PATH))

    assert dnf_conf.items('main') == {
        'gpgcheck': '1',
        'installonly_limit': '3',
        'clean_requirements_on_remove': 'True',
        'best': 'False',
        'skip_if_unavailable': 'True'
    }

    assert dnf_conf.items('rhel-7-server-rhn-tools-beta-debug-rpms') == {
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

    assert dnf_conf.file_name == 'dnf.conf'
    assert dnf_conf.file_path == '/etc/dnf/dnf.conf'
