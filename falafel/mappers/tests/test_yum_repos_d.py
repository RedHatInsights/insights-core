from falafel.mappers import yum_repos_d
from falafel.tests import context_wrap


REPOINFO = '''
[rhel-source]
name=Red Hat Enterprise Linux $releasever - $basearch - Source
baseurl=ftp://ftp.redhat.com/pub/redhat/linux/enterprise/$releasever/en/os/SRPMS/
enabled=0
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release

[rhel-source-beta]
name=Red Hat Enterprise Linux $releasever Beta - $basearch - Source
baseurl=ftp://ftp.redhat.com/pub/redhat/linux/beta/$releasever/en/os/SRPMS/
enabled=0
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-beta,file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release
'''

REPOPATH = 'etc/yum.repos.d/rhel-source.repo'


class TestYumReposD():
    def test_yum_repos_d(self):
        repos_info = yum_repos_d.yum_repos_d(context_wrap(REPOINFO, path=REPOPATH))

        assert len(repos_info.data) == 2

        assert repos_info.data['rhel-source'] == {'name': 'Red Hat Enterprise Linux $releasever - $basearch - Source',
                                                  'baseurl': 'ftp://ftp.redhat.com/pub/redhat/linux/enterprise/$releasever/en/os/SRPMS/',
                                                  'enabled': '0',
                                                  'gpgcheck': '1',
                                                  'gpgkey': 'file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release'}
        assert repos_info.data['rhel-source-beta'] == {'name': 'Red Hat Enterprise Linux $releasever Beta - $basearch - Source',
                                                       'baseurl': 'ftp://ftp.redhat.com/pub/redhat/linux/beta/$releasever/en/os/SRPMS/',
                                                       'enabled': '0',
                                                       'gpgcheck': '1',
                                                       'gpgkey': 'file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-beta,file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release'}
        assert repos_info.file_name == 'rhel-source.repo'
        assert repos_info.file_path == 'etc/yum.repos.d/rhel-source.repo'
