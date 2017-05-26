from .. import Mapper, LegacyItemAccess, mapper
from ..mappers.pam import PamDConf
from ..mappers import split_kv_pairs


@mapper('vsftpd')
class VsftpdPamConf(PamDConf):
    """Parsing for `/etc/pam.d/vsftpd`. """
    pass


@mapper('vsftpd.conf')
class VsftpdConf(Mapper, LegacyItemAccess):
    """Parsing for `/etc/vsftpd.conf`

    Reference:
        https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/3/html/Reference_Guide/s1-ftp-vsftpd-conf.html
    """
    def parse_content(self, content):
        self.data = split_kv_pairs(content, ordered=True)
