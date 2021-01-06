"""
Libssh configuration files
==========================

This module provides the ssh options in libssh configuration file

Parsers provided by this module are:

LibsshClientConfig - file ``/etc/libssh/libssh_client.config``
--------------------------------------------------------------

LibsshServerConfig - file ``/etc/libssh/libssh_server.config``
--------------------------------------------------------------
"""

from insights.specs import Specs
from insights.core import CommandParser
from .. import parser, get_active_lines
from insights.parsers import SkipException


class LibsshConfig(CommandParser, dict):
    """
    Base class for libssh configuration file.

    There are many options in the libssh configuration file and
    all of them are stored in one of the following formations:
    a)   Key  [space]  Value
    b)   Key  =  Value

    There are the keywords used in the configuration file:
        include
        hostkey
        listenaddress
        port
        loglevel
        ciphers
        macs
        kexalgorithms
        match
        pubkeyacceptedkeytypes
        hostkeyalgorithms
        all
        user
        group
        host
        localaddress
        localport
        rdomain
        address

    Sample output::

        # Parse system-wide crypto configuration file
        Include /etc/crypto-policies/back-ends/libssh.config
        # Parse OpenSSH configuration file for consistency
        Include /etc/ssh/sshd_config

    .. note::

        If there are two or more lines that have the same key, then we
        store the values in a list.

    Examples:
        >>> 'Include' in config
        True
        >>> config['Include']
        ['/etc/crypto-policies/back-ends/libssh.config', '/etc/ssh/sshd_config']

    Raises:
        SkipException: When input content is empty or there is a syntax error.
    """

    def parse_content(self, content):
        if not content:
            raise SkipException('No content.')

        for line in get_active_lines(content):
            delimiter = None
            if ' ' in line:
                delimiter = ' '

            if '=' in line:
                delimiter = '='

            try:
                k, v = [i.strip() for i in line.split(delimiter)]
                if k not in self:
                    self[k] = v
                else:
                    _v = self[k]
                    _v = [_v] if not isinstance(_v, list) else _v
                    if v not in _v:
                        _v.append(v)
                        self[k] = _v
            except ValueError:
                raise SkipException('Syntax error')


@parser(Specs.libssh_client_config)
class LibsshClientConfig(LibsshConfig):
    """
    Parser for accessing the ``/etc/libssh/libssh_client.config`` file.

    .. note::

        Please refer to the super-class :py:class:`insights.parsers.libssh_config:LibsshConfig`
        for more usage information.
    """
    pass


@parser(Specs.libssh_server_config)
class LibsshServerConfig(LibsshConfig):
    """
    Parser for accessing the ``/etc/libssh/libssh_server.config`` file

    .. note::

        Please refer to the super-class :py:class:`insights.parsers.libssh_config:LibsshConfig`
        for more usage information.
    """
    pass
