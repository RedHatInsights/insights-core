"""
LoginPamConf - file ``/etc/pam.d/login``
========================================
"""

from insights import parser
from insights.parsers.pam import PamDConf
from insights.specs import Specs


@parser(Specs.login_pam_conf)
class LoginPamConf(PamDConf):
    """
    Parse the `/etc/pam.d/login` PAM configuration file.

    See the :py:class:`insights.parsers.pam.PamDConf` class documentation for
    more information on how this class is used.

    Sample PAM configuration for login service::

        #%PAM-1.0
        auth [user_unknown=ignore success=ok ignore=ignore default=bad] pam_securetty.so
        auth       substack     system-auth
        auth       include      postlogin
        account    required     pam_nologin.so
        account    include      system-auth
        password   include      system-auth
        # pam_selinux.so close should be the first session rule
        session    required     pam_selinux.so close
        session    required     pam_loginuid.so
        session    optional     pam_console.so

    Examples:
        >>> login_pam_conf[0].interface
        'auth'
        >>> login_pam_conf[0].control_flags[0]
        ControlFlag(flag='user_unknown', value='ignore')
        >>> login_pam_conf[0].module_name
        'pam_securetty.so'
        >>> login_pam_conf[6].module_args
        'close'
    """
    pass
