from falafel.core.plugins import mapper
from falafel.core import MapperOutput
from falafel.mappers import get_active_lines


class YumReposD(MapperOutput):
    pass


@mapper('yum.repos.d')
def yum_repos_d(context):
    '''
    Return a object contains a dict.
    There are several files in 'yum.repos.d' directory, which have the same format.
    For example:
    --------one of the files : rhel-source.repo---------
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
    ----------------------------------------------------
    The output's dict will looks like:
    {
        "rhel-source-beta": {
            "gpgcheck": "1",
            "gpgkey": "file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-beta,file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release",
            "enabled": "0",
            "name": "Red Hat Enterprise Linux $releasever Beta - $basearch - Source",
            "baseurl": "ftp://ftp.redhat.com/pub/redhat/linux/beta/$releasever/en/os/SRPMS/"
        },
        "rhel-source": {
            "gpgcheck": "1",
            "gpgkey": "file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release",
            "enabled": "0",
            "name": "Red Hat Enterprise Linux $releasever - $basearch - Source",
            "baseurl": "ftp://ftp.redhat.com/pub/redhat/linux/enterprise/$releasever/en/os/SRPMS/"
        }
    }
    '''
    repos = {}
    section = None
    info = {}

    for line in get_active_lines(context.content):
        if section:
            if line.startswith('['):
                repos[section] = info
                section = line[1:-1]
                info = {}
                continue
            else:
                key, val = line.split("=", 1)
                info[key.strip()] = val.strip()
        else:
            # assign the first line to first section
            section = line[1:-1]
    # Some files contain nothing.
    if section:
        # Add the last section
        repos[section] = info
    return YumReposD(repos, path=context.path)
