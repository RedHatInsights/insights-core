import re
import string

from .. import Parser, parser, LegacyItemAccess
from insights.specs import Specs
from insights.parsr import (Char, EOF, HangingString, InSet, Many, OneLineComment, Opt,
                            skip_none, String, WithIndent, WS)


header_chars = (set(string.printable) - set(string.whitespace) - set("[]")) | set(" ")
sep_chars = set(":=")
key_chars = header_chars - sep_chars - set(" ")
value_chars = set(string.printable) - set("\n\r")

LeftEnd = WS >> Char("[") << WS
RightEnd = WS >> Char("]") << WS
Header = LeftEnd >> String(header_chars) << RightEnd
Key = WS >> String(key_chars) << WS
Sep = InSet(sep_chars)
Value = WS >> HangingString(value_chars)
KVPair = WithIndent(Key + Opt(Sep >> Value))
Comment = WS >> (OneLineComment("#") | OneLineComment(";")).map(lambda x: None)

Line = Comment | KVPair.map(tuple)
Sect = (Header + Many(Line).map(skip_none).map(dict)).map(tuple)
Doc = Many(Comment | Sect).map(skip_none).map(dict)
Top = Doc << WS << EOF


def parse_yum_repos(content):
    doc = Top(content)
    for k, v in doc.items():
        for special in ("baseurl", "gpgkey"):
            if special in v:
                v[special] = [i.strip() for i in re.split(",| ", v[special])]
    return doc


@parser(Specs.yum_repos_d)
class YumReposD(LegacyItemAccess, Parser):
    """Class to parse the files under ``yum.repos.d`` """

    def get(self, key):
        return self.data.get(key)

    def parse_content(self, content):
        """
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
        """
        self.data = parse_yum_repos("\n".join(content))

    def __iter__(self):
        for repo in self.data:
            yield repo
