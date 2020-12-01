"""
Postconf - command ``postconf``
===============================

PostconfBuiltin - command ``postconf -C builtin``
=================================================
"""

from insights.core import CommandParser
from insights.core.plugins import parser
from insights.specs import Specs
from insights.parsers import SkipException


class _Postconf(CommandParser, dict):
    """
    Class for parsing the ``postconf`` command.
    Sample input::

        smtpd_tls_loglevel = 0
        smtpd_tls_mandatory_ciphers = medium
        smtpd_tls_mandatory_exclude_ciphers =
        smtpd_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1

    Examples:
        >>> type(_postconf)
        <class 'insights.parsers.postconf._Postconf'>
        >>> _postconf['smtpd_tls_loglevel'] == '0'
        True
        >>> _postconf['smtpd_tls_mandatory_ciphers'] == 'medium'
        True
        >>> _postconf['smtpd_tls_mandatory_exclude_ciphers'] == ''
        True
        >>> _postconf['smtpd_tls_mandatory_protocols'] == '!SSLv2, !SSLv3, !TLSv1'
        True
    """

    def parse_content(self, content):
        if not content:
            raise SkipException

        data = dict()
        for line in content:
            if '=' in line:
                key, value = [i.strip() for i in line.split('=', 1)]
                data[key] = value

        if not data:
            raise SkipException

        self.update(data)


@parser(Specs.postconf_builtin)
class PostconfBuiltin(_Postconf):
    """
    Class for parsing the ``postconf -C builtin`` command.
    Sample input::

        smtpd_tls_loglevel = 0
        smtpd_tls_mandatory_ciphers = medium
        smtpd_tls_mandatory_exclude_ciphers =
        smtpd_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1

    Examples:
        >>> type(postconfb)
        <class 'insights.parsers.postconf.PostconfBuiltin'>
        >>> postconfb['smtpd_tls_loglevel'] == '0'
        True
        >>> postconfb['smtpd_tls_mandatory_ciphers'] == 'medium'
        True
        >>> postconfb['smtpd_tls_mandatory_exclude_ciphers'] == ''
        True
        >>> postconfb['smtpd_tls_mandatory_protocols'] == '!SSLv2, !SSLv3, !TLSv1'
        True
    """


@parser(Specs.postconf)
class Postconf(_Postconf):
    """
    Class for parsing the ``postconf`` command.
    Sample input::

        smtpd_tls_loglevel = 0
        smtpd_tls_mandatory_ciphers = medium
        smtpd_tls_mandatory_exclude_ciphers =
        smtpd_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1

    Examples:
        >>> type(postconf)
        <class 'insights.parsers.postconf.Postconf'>
        >>> postconf['smtpd_tls_loglevel'] == '0'
        True
        >>> postconf['smtpd_tls_mandatory_ciphers'] == 'medium'
        True
        >>> postconf['smtpd_tls_mandatory_exclude_ciphers'] == ''
        True
        >>> postconf['smtpd_tls_mandatory_protocols'] == '!SSLv2, !SSLv3, !TLSv1'
        True
    """
