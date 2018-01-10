"""
Parsers for VSFTPD configuration
================================

This module contains two parsers:

VsftpdPamConf - file ``/etc/pam.d/vsftpd``
------------------------------------------

VsftpdConf - file ``/etc/vsftpd.conf``
--------------------------------------

"""

from .. import Parser, LegacyItemAccess, parser
from ..parsers.pam import PamDConf
from ..parsers import split_kv_pairs
from insights.specs import Specs


@parser(Specs.vsftpd)
class VsftpdPamConf(PamDConf):
    """
    Parsing for the `/etc/pam.d/vsftpd` PAM configuration.

    See the :py:class:`insights.parsers.pam.PamDConf` class documentation for
    more information on how this class is used.

    Sample PAM configuration for vsftpd::

        #%PAM-1.0
        session    optional     pam_keyinit.so    force revoke
        auth       required     pam_listfile.so item=user sense=deny file=/etc/vsftpd/ftpusers onerr=succeed
        auth       required     pam_shells.so
        auth       include      password-auth
        account    include      password-auth
        session    required     pam_loginuid.so
        session    include      password-auth

    Examples:
        >>> vs_pam = shared[VsftpdPamConf]
        >>> vs_pam[0]
        <insights.parsers.pam.PamConfEntry at 0x15c6cd0>
        >>> vs_pam[0].interface
        'session'
        >>> vs_pam[0].control_flags
        [ControlFlag(flag='optional', value=None)]
        >>> vs_pam[0].control_flags[0].flag
        'optional'
        >>> vs_pam[0].module_name
        'pam_keyinit.so'
        >>> vs_pam[0].module_args
        'force revoke'
    """
    pass


@parser(Specs.vsftpd_conf)
class VsftpdConf(Parser, LegacyItemAccess):
    """
    Parsing for `/etc/vsftpd.conf`.  Key=value pairs are stored in a
    dictionary, made available directly through the object itself thanks to
    the :py:class:`insights.core.LegacyItemAccess` mixin.

    Reference:
        https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/3/html/Reference_Guide/s1-ftp-vsftpd-conf.html

    Sample content::

        # No anonymous login
        anonymous_enable=NO
        # Let local users login
        local_enable=YES

        # Write permissions
        write_enable=YES

    Examples:
        >>> conf = shared[VsftpdConf]
        >>> 'anonymous_enable' in conf
        True
        >>> 'chmod_enable' in conf
        False
        >>> conf['anonymous_enable']
        'NO'
    """
    def parse_content(self, content):
        self.data = split_kv_pairs(content, ordered=True)
