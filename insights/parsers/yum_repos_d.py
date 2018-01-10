from .. import Parser, parser, get_active_lines, LegacyItemAccess
from insights.specs import Specs


@parser(Specs.yum_repos_d)
class YumReposD(LegacyItemAccess, Parser):
    """Class to parse the files under ``yum.repos.d`` """

    def get(self, key):
        return self.data.get(key)

    def parse_content(self, content):
        '''
        Return an object contains a dict.
        {
            "rhel-source": {
                "gpgcheck": "1",
                "gpgkey": ["file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release",
                           "file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release_bak"]
                "enabled": "0",
                "name": "Red Hat Enterprise Linux $releasever - $basearch - Source",
                "baseurl": "ftp://ftp.redhat.com/pub/redhat/linux/enterprise/$releasever/en/os/SRPMS/"
            }
        }
        ----------------------------------------------------
        There are several files in 'yum.repos.d' directory, which have the same
        format.  For example:
        --------one of the files : rhel-source.repo---------
        [rhel-source]
        name=Red Hat Enterprise Linux $releasever - $basearch - Source
        baseurl=ftp://ftp.redhat.com/pub/redhat/linux/enterprise/$releasever/en/os/SRPMS/
        enabled=0
        gpgcheck=1
        gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release
               file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release_bak
        '''
        repos_dict = {}
        section_dict = {}
        key = None
        for line in get_active_lines(content):
            if line.startswith('['):
                section_dict = {}
                repos_dict[line[1:-1]] = section_dict
            elif '=' in line:
                key, value = [s.strip() for s in line.split("=", 1)]
                if key in ('baseurl', 'gpgkey'):
                    section_dict[key] = [v.strip() for v in value.split(",")]
                else:
                    section_dict[key] = value
            else:
                if key and isinstance(section_dict[key], list):
                    section_dict[key].extend(v.strip() for v in line.split(","))
                # Otherwise ignore line if no key or we don't store multiple values
        self.data = repos_dict

    def __iter__(self):
        for repo in self.data:
            yield repo
