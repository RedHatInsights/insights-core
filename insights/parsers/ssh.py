"""
SshDConfig - file ``/etc/ssh/sshd_config``
==========================================

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
    >>> from insights.tests import context_wrap
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
    >>> sshd_config.get_line('ListenAddress')
    'ListenAddress 10.110.1.1'
    >>> sshd_config.get_values('ListenAddress')
    ['10.110.0.1', '10.110.1.1']
    >>> sshd_config.get_values('ListenAddress', default='0.0.0.0')
    ['10.110.0.1', '10.110.1.1']
    >>> sshd_config.get_values('ListenAddress', join_with=',')
    '10.110.0.1,10.110.1.1'
"""
from collections import namedtuple
from .. import Parser, parser, get_active_lines


@parser('sshd_config')
class SshDConfig(Parser):
    """Parsing for ``/etc/ssh/sshd_config`` file.

    Properties:
        lines (list): List of `KeyValue` namedtupules for each line in
            the configuration file.
        keywords (set): Set of keywords present in the configuration
            file, each keyword has been converted to lowercase.
    """

    KeyValue = namedtuple('KeyValue', ['keyword', 'value', 'kw_lower', 'line'])
    """namedtuple: Represent name value pair as a namedtuple with case ."""

    # TODO: add support for "+" options in sshd_config once the support for
    # such options is added to the openssh versions shipped in RHEL. These
    # options allow a sshd_config line such as "Ciphers +arcfour", which means
    # "take the built-in defaults and add arcfour to them". Currently (as of
    # 2016-11), the "+" options are not supported by any openssh-server
    # version officially shipped in RHEL and it is unclear whether these
    # options will be backported. There are hints that they might be
    # backported in the future, hence this note.
    def parse_content(self, content):
        self.lines = []
        for line in get_active_lines(content):
            kw, val = [s.strip() for s in line.split(None, 1)]
            self.lines.append(self.KeyValue(
                kw, val, kw.lower(), line
            ))
        self.keywords = set([k.kw_lower for k in self.lines])

    def __contains__(self, keyword):
        """
        (bool) Is this keyword found in the configuration file?
        """
        return keyword.lower() in self.keywords

    def __iter__(self):
        """
        (iter) Yields a list of all the lines in the configuration file that
        actually contained a configuration option.
        """
        for line in self.lines:
            yield line

    def __getitem__(self, keyword):
        """
        (list) Get all values of this keyword.
        """
        kw = keyword.lower()
        if kw in self.keywords:
            return [kv.value for kv in self.lines if kv.kw_lower == kw]

    def get(self, keyword):
        """
        Get all declarations of this keyword in the configuration file.

        Returns:
            (list): a list of named tuples with the following properties:
                - ``keyword`` - the keyword as given on that line
                - ``value`` - the value of the keyword
                - ``kw_lower`` - the keyword converted to lower case
                - ``line`` - the complete line as found in the config file
        """
        kw = keyword.lower()
        return [kv for kv in self.lines if kv.kw_lower == kw]

    def get_values(self, keyword, default='', join_with=None, split_on=None):
        """
        Get all the values assigned to this keyword.

        Firstly, if the keyword is not found in the configuration file, the
        value of the ``default`` option is used (defaulting to ``''``).

        Then, if the ``join_with`` option is given, this string is used to
        join the values found on each separate definition line.  Otherwise,
        each separate definition line is returned as a string.

        Finally, if the ``split_on`` option is given, this string is used to
        split the combined string above into a list.  Otherwise, the combined
        string is returned as is.
        """
        kw = keyword.lower()
        if kw in self.keywords:
            vals = [kv.value for kv in self.lines if kv.kw_lower == kw]
        else:
            vals = [default]
        # Should we join them together?
        if join_with is None:
            return vals
        # OK, join them together.
        val_str = join_with.join(vals)
        # Should we now split them?
        if split_on is None:
            return val_str
        else:
            return val_str.split(split_on)

    def get_line(self, keyword, default=''):
        """
        (str): Get the line with the last declarations of this keyword in the
        configuration file, optionally pretending that we had a line with the
        default value and a comment informing the user that this was a
        created default line.

        This is a hack, but it's commonly used in the sshd configuration
        because of the many lines that are commonly omitted because they
        have their default value.

        Parameters:
            keyword(str): Keyword to find
            default: optional value to supply if not found
        """
        lines = self.get(keyword)
        if lines:
            return lines[-1].line
        else:
            return "{keyword} {value}  # Implicit default".format(
                keyword=keyword, value=default
            )

    def last(self, keyword, default=None):
        """
        str: Returns the value of the last keyword found in config.

        Parameters:
            keyword(str): Keyword to find
            default: optional value to supply if not found
        """
        entries = self.__getitem__(keyword)
        if entries:
            return entries[-1]
        else:
            return default
