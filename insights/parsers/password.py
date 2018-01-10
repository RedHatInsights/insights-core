from .. import parser
from ..parsers.pam import PamDConf
from insights.specs import Specs


@parser(Specs.password_auth)
class PasswordAuthPam(PamDConf):
    """Parsing for `/etc/pam.d/password-auth`. """
    pass
