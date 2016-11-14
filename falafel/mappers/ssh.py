"""
ssh - Files for configuration of `ssh`
======================================

The ``ssh`` module provides parsing for the ``sshd_config``
file.  The ``SshDConfig`` class implements the parsing and
provides a ``list`` of all configuration lines present in
the file.

Sample input is provided in the *Examples*.

Examples:
    >>> sshd_config_input = '''
    ... #	$OpenBSD: sshd_config,v 1.93 2014/01/10 05:59:19 djm Exp $
    ...
    ... Port 22
    ... #AddressFamily any
    ... ListenAddress 10.110.0.1
    ... Port 22
    ... ListenAddress 10.110.1.1
    ... #ListenAddress ::
    ...
    ... # The default requires explicit activation of protocol 1
    ... #Protocol 2
    ... Protocol 1
    ... '''.strip()
    >>> from falafel.tests import context_wrap
    >>> shared = {SshDConfig: SshDConfig(context_wrap(sshd_config_input))}
    >>> sshd_config = shared[SshDConfig]
    >>> 'Port' in sshd_config
    True
    >>> 'PORT' in sshd_config
    True
    >>> 'AddressFamily' in sshd_config
    False
    >>> sshd_config['port']
    ['22', '22']
    >>> sshd_config['Protocol']
    ['1']
    >>> [line for line in sshd_config if line.keyword == 'Port']
    [KeyValue(keyword='Port', value='22', kw_lower='port'), KeyValue(keyword='Port', value='22', kw_lower='port')]
    >>> sshd_config.last('ListenAddress')
    '10.110.1.1'
"""
from collections import namedtuple
from .. import Mapper, mapper, get_active_lines


@mapper('sshd_config')
class SshDConfig(Mapper):
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
            kw, val = line.split(None, 1)
            self.lines.append(self.KeyValue(kw.strip(), val.strip(), kw.lower().strip()))
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


if __name__ == '__main__':
    import doctest
    doctest.testmod()
