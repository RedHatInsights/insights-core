"""
Parsers for VSFTPD configuration
================================

This module contains two parsers:

VsftpdPamConf - file ``/etc/pam.d/vsftpd``
------------------------------------------

VsftpdConf - file ``/etc/vsftpd.conf``
--------------------------------------

"""

from insights import Parser, LegacyItemAccess, parser
from insights.core import ContainerParser
from insights.parsers.pam import PamDConf
from insights.parsers import split_kv_pairs
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
        >>> vsftpd_pam_conf[0].interface
        'session'
        >>> vsftpd_pam_conf[0].control_flags
        [ControlFlag(flag='optional', value=None)]
        >>> vsftpd_pam_conf[0].control_flags[0].flag
        'optional'
        >>> vsftpd_pam_conf[0].module_name
        'pam_keyinit.so'
        >>> vsftpd_pam_conf[0].module_args
        'force revoke'
    """
    pass


@parser(Specs.vsftpd_conf)
class VsftpdConf(Parser, LegacyItemAccess):
    """
    Parsing for `/etc/vsftpd/vsftpd.conf`.  Key=value pairs are stored in a
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
        >>> 'anonymous_enable' in vsftpd_conf
        True
        >>> 'chmod_enable' in vsftpd_conf
        False
        >>> vsftpd_conf['anonymous_enable']
        'NO'
    """
    def parse_content(self, content):
        self.data = split_kv_pairs(content, ordered=True)


@parser(Specs.container_vsftpd_conf)
class ContainerVsftpdConf(ContainerParser, VsftpdConf):
    """
    Parsing for `/etc/vsftpd/vsftpd.conf` from the containers.  Key=value pairs are stored in a
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
        >>> type(container_vsftpd_conf)
        <class 'insights.parsers.vsftpd.ContainerVsftpdConf'>
        >>> container_vsftpd_conf.container_id
        '2869b4e2541c'
        >>> container_vsftpd_conf.image
        'registry.access.redhat.com/ubi8/nginx-120'
        >>> 'anonymous_enable' in container_vsftpd_conf
        True
        >>> 'chmod_enable' in container_vsftpd_conf
        False
        >>> container_vsftpd_conf['anonymous_enable']
        'NO'
    """
    pass
