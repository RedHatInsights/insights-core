from .. import mapper
from ..mappers.pam import PamDConf


@mapper('password-auth')
class PasswordAuthPam(PamDConf):
    """Parsing for `/etc/pam.d/password-auth`. """
    pass
