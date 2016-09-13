from falafel.mappers.yum_repos_d import YumReposD
from falafel.tests import context_wrap


REPOINFO = '''
[rhel-source]
name=Red Hat Enterprise Linux $releasever - $basearch - Source
baseurl=ftp://ftp.redhat.com/pub/redhat/linux/enterprise/$releasever/en/os/SRPMS/
enabled=0
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release
 file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release1

[rhel-source-beta]
name=Red Hat Enterprise Linux $releasever Beta - $basearch - Source
baseurl=ftp://ftp.redhat.com/pub/redhat/linux/beta/$releasever/en/os/SRPMS/
enabled=0
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-beta
       file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release
'''

REPOPATH = 'etc/yum.repos.d/rhel-source.repo'


def test_yum_repos_d():
    repos_info = YumReposD.parse_context(context_wrap(REPOINFO, path=REPOPATH))

    print repos_info.get('rhel-source')
    assert repos_info.get('rhel-source') == {
            'name': 'Red Hat Enterprise Linux $releasever - $basearch - Source',
            'baseurl': ['ftp://ftp.redhat.com/pub/redhat/linux/enterprise/$releasever/en/os/SRPMS/'],
            'enabled': '0',
            'gpgcheck': '1',
            'gpgkey': ['file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release',
                       'file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release1']}
    assert repos_info.get('rhel-source-beta') == {
            'name': 'Red Hat Enterprise Linux $releasever Beta - $basearch - Source',
            'baseurl': ['ftp://ftp.redhat.com/pub/redhat/linux/beta/$releasever/en/os/SRPMS/'],
            'enabled': '0',
            'gpgcheck': '1',
            'gpgkey': ['file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-beta',
                       'file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release']}
    assert repos_info.file_name == 'rhel-source.repo'
    assert repos_info.file_path == 'etc/yum.repos.d/rhel-source.repo'
