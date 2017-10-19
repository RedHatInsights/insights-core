from .. import parser
from ..parsers.pam import PamDConf
from insights.specs import password_auth


@parser(password_auth)
class PasswordAuthPam(PamDConf):
    """Parsing for `/etc/pam.d/password-auth`. """
    pass
