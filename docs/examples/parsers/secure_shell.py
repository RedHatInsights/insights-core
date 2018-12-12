"""
secure_shell - Files for configuration of `ssh`
===============================================

The ``secure_shell`` module provides parsing for the ``sshd_config``
file.  The ``SshDConfig`` class implements the parsing and
provides a ``list`` of all configuration lines present in
the file.

Sample content from the ``/etc/sshd/sshd_config`` file is::

    #   $OpenBSD: sshd_config,v 1.93 2014/01/10 05:59:19 djm Exp $

    Port 22
    #AddressFamily any
    ListenAddress 10.110.0.1
    Port 22
    ListenAddress 10.110.1.1
    #ListenAddress ::

    # The default requires explicit activation of protocol 1
    #Protocol 2
    Protocol 1

Examples:
    >>> 'Port' in sshd_config
    True
    >>> 'PORT' in sshd_config  # items are stored case-insentive
    True
    >>> 'AddressFamily' in sshd_config  # comments are ignored
    False
    >>> sshd_config['port']  # All value stored by keyword in lists
    ['22', '22']
    >>> sshd_config['Protocol']  # Single items have one list element
    ['1']
    >>> [line for line in sshd_config if line.keyword == 'Port']  # can be used as an iterator
    [KeyValue(keyword='Port', value='22', kw_lower='port'), KeyValue(keyword='Port', value='22', kw_lower='port')]
    >>> sshd_config.last('ListenAddress')  # Easy way of finding the current configuration for a single item
    '10.110.1.1'
"""
from collections import namedtuple
from insights import Parser, parser, get_active_lines
from insights.core.spec_factory import SpecSet, simple_file
import os


class LocalSpecs(SpecSet):
    """ Datasources for collection from test file """
    conf_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sshd_config')

    sshd_config = simple_file(conf_file)


@parser(LocalSpecs.sshd_config)
class SshDConfig(Parser):
    """Parsing for ``sshd_config`` file.

    Attributes:
        lines (list): List of `KeyValue` namedtupules for each line in
            the configuration file.
        keywords (set): Set of keywords present in the configuration
            file, each keyword has been converted to lowercase.
    """

    KeyValue = namedtuple('KeyValue', ['keyword', 'value', 'kw_lower'])
    """namedtuple: Represent name value pair as a namedtuple with case ."""

    def parse_content(self, content):
        self.lines = []
        for line in get_active_lines(content):
            kw, val = (w.strip() for w in line.split(None, 1))
            self.lines.append(self.KeyValue(kw, val, kw.lower()))
        self.keywords = set([k.kw_lower for k in self.lines])

    def __contains__(self, keyword):
        return keyword.lower() in self.keywords

    def __iter__(self):
        for line in self.lines:
            yield line

    def __getitem__(self, keyword):
        kw = keyword.lower()
        if kw in self.keywords:
            return [kv.value for kv in self.lines if kv.kw_lower == kw]

    def last(self, keyword):
        """str: Returns the value of the last keyword found in config."""
        entries = self.__getitem__(keyword)
        if entries:
            return entries[-1]
