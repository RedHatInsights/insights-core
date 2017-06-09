from .. import parser
from ..parsers.pam import PamDConf


@parser('password-auth')
class PasswordAuthPam(PamDConf):
    """Parsing for `/etc/pam.d/password-auth`. """
    pass
