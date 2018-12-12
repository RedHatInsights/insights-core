"""
SshConfig - file for ``ssh client config``
==========================================

This module contains parsers that check the ssh client config files.

Parsers provided by this module are:

EtcSshConfig - file ``/etc/ssh/ssh_config``
-------------------------------------------

ForemanSshConfig - file ``/usr/share/foreman/.ssh/ssh_config``
--------------------------------------------------------------

"""
from collections import namedtuple

from insights.specs import Specs

from .. import Parser, get_active_lines, parser


class SshClientConfig(Parser):
    """Base class for sshclient config file."""

    def __init__(self, context):
        self.global_lines = []
        self.host_lines = {}
        super(SshClientConfig, self).__init__(context)

    def _split_content(self, content):
        index = [i for i, l in enumerate(get_active_lines(content)) if l.startswith('Host ')]
        if not index:
            self._global_content = get_active_lines(content)
            self._host_content = []
        else:
            if index:
                self._global_content = get_active_lines(content)[0:index[0]]
                self._host_content = get_active_lines(content)[index[0]:]

    KeyValue = namedtuple('KeyValue', ['keyword', 'value', 'line'])

    def parse_content(self, content):
        self._split_content(content)
        for line in self._global_content:
            line_splits = [s.strip() for s in line.split(None, 1)]
            kw, val = line_splits[0], line_splits[1] if len(line_splits) == 2 else ''
            self.global_lines.append(self.KeyValue(kw, val, line))

        hostbit = ''
        for line in self._host_content:
            line_splits = [s.strip() for s in line.split(None, 1)]
            kw, val = line_splits[0], line_splits[1] if len(line_splits) == 2 else ''
            if kw == 'Host':
                hostbit = kw + '_' + val
                self.host_lines[hostbit] = []
            else:
                self.host_lines[hostbit].append(self.KeyValue(kw, val, line))

        del self._global_content
        del self._host_content
        return


@parser(Specs.ssh_config)
class EtcSshConfig(SshClientConfig):
    """
    This parser reads the file ``/etc/ssh/ssh_config``

    Sample output::

        #   ProxyCommand ssh -q -W %h:%p gateway.example.com
        #   RekeyLimit 1G 1h
        #
        # Uncomment this if you want to use .local domain
        # Host *.local
        #   CheckHostIP no
        ProxyCommand ssh -q -W %h:%p gateway.example.com

        Host *
            GSSAPIAuthentication yes
        # If this option is set to yes then remote X11 clients will have full access
        # to the original X11 display. As virtually no X11 client supports the untrusted
        # mode correctly we set this to yes.
            ForwardX11Trusted yes
        # Send locale-related environment variables
            SendEnv LANG LC_CTYPE LC_NUMERIC LC_TIME LC_COLLATE LC_MONETARY LC_MESSAGES
            SendEnv LC_PAPER LC_NAME LC_ADDRESS LC_TELEPHONE LC_MEASUREMENT
            SendEnv LC_IDENTIFICATION LC_ALL LANGUAGE
            SendEnv XMODIFIERS

        Host proxytest
            HostName 192.168.122.2

    Examples:
        >>> len(etcsshconfig.global_lines)
        1
        >>> 'Host_*' in etcsshconfig.host_lines
        True
        >>> etcsshconfig.host_lines['Host_*'][0].keyword
        'GSSAPIAuthentication'
        >>> etcsshconfig.host_lines['Host_proxytest'][0].value
        '192.168.122.2'
    """
    pass


@parser(Specs.ssh_foreman_config)
class ForemanSshConfig(SshClientConfig):
    """
    This parser reads the file ``/usr/share/foreman/.ssh/ssh_config``

    Sample output::

        #   ProxyCommand ssh -q -W %h:%p gateway.example.com
        #   RekeyLimit 1G 1h
        #
        # Uncomment this if you want to use .local domain
        # Host *.local
        #   CheckHostIP no
        ProxyCommand ssh -q -W %h:%p gateway.example.com

        Host *
            GSSAPIAuthentication yes
        # If this option is set to yes then remote X11 clients will have full access
        # to the original X11 display. As virtually no X11 client supports the untrusted
        # mode correctly we set this to yes.
            ForwardX11Trusted yes
        # Send locale-related environment variables
            SendEnv LANG LC_CTYPE LC_NUMERIC LC_TIME LC_COLLATE LC_MONETARY LC_MESSAGES
            SendEnv LC_PAPER LC_NAME LC_ADDRESS LC_TELEPHONE LC_MEASUREMENT
            SendEnv LC_IDENTIFICATION LC_ALL LANGUAGE
            SendEnv XMODIFIERS

        Host proxytest
            HostName 192.168.122.2

    Examples:
        >>> len(foremansshconfig.global_lines)
        1
        >>> 'Host_*' in foremansshconfig.host_lines
        True
        >>> foremansshconfig.host_lines['Host_*'][0].keyword
        'GSSAPIAuthentication'
        >>> foremansshconfig.host_lines['Host_proxytest'][0].value
        '192.168.122.2'
    """
    pass
