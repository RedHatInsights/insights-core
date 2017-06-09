from .. import Parser, LegacyItemAccess, parser
from ..parsers.pam import PamDConf
from ..parsers import split_kv_pairs


@parser('vsftpd')
class VsftpdPamConf(PamDConf):
    """Parsing for `/etc/pam.d/vsftpd`. """
    pass


@parser('vsftpd.conf')
class VsftpdConf(Parser, LegacyItemAccess):
    """Parsing for `/etc/vsftpd.conf`

    Reference:
        https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/3/html/Reference_Guide/s1-ftp-vsftpd-conf.html
    """
    def parse_content(self, content):
        self.data = split_kv_pairs(content, ordered=True)
