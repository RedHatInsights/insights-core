"""
Parsers for SSH configuration
=============================

SshDConfig - file ``/etc/ssh/sshd_config``
------------------------------------------

SshDConfigD - file ``/etc/ssh/sshd_config.d/*.conf``
----------------------------------------------------

SshdTestMode - command ``sshd -T``
----------------------------------
"""
from collections import namedtuple
from .. import Parser, parser, get_active_lines
from insights.specs import Specs
import re

# optional whitespace, at least one non-whitespace (the keyword), at least one whitespace (space), a plus literal, anything
PLUS_PATTERN = re.compile(r'^\s*\S+\s+\+.*$')


@parser(Specs.sshd_config)
class SshDConfig(Parser):
    """
    Parsing for ``/etc/ssh/sshd_config`` file.

    The ``ssh`` module provides parsing for the ``sshd_config``
    file.  The ``SshDConfig`` class implements the parsing and
    provides a ``list`` of all configuration lines present in
    the file.

    Sample input is provided in the *Examples*.

    Examples:
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
        [KeyValue(keyword='Port', value='22', kw_lower='port', line='Port 22'), KeyValue(keyword='Port', value='22', kw_lower='port', line='Port 22')]
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

    Properties:
        lines (list): List of `KeyValue` namedtupules for each line in
            the configuration file.
        keywords (set): Set of keywords present in the configuration
            file, each keyword has been converted to lowercase.
    """

    KeyValue = namedtuple('KeyValue', ['keyword', 'value', 'kw_lower', 'line'])
    """namedtuple: Represent name value pair as a namedtuple with case ."""

    # Note about "+" options. In some openssh versions and for some keywords,
    # a "+" at the beginning of the value list signifies that the values are
    # added to the default list of values.
    # IT IS NOT DETECTED AND PARSED HERE.
    # `parse_content()` doesn't split the individual values because some
    # keywords don't have a list of values (just one string).
    # See the docstring in `line_uses_plus()` for more details.
    # Re: BZ#1697477
    # Config lines may also be delimited by `=`, and values may be quoted
    # with `"`. Here it is assumed that config lines are well-formed.

    def parse_content(self, content):
        self.lines = []
        for line in get_active_lines(content):
            line_splits = [s.strip() for s in re.split(r"[\s=]+", line, 1)]
            kw, val = line_splits[0], line_splits[1].strip('"') if \
                len(line_splits) == 2 else ''
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

    def line_uses_plus(self, keyword):
        """
        (union[bool, None]): Get the line with the last declarations of this
        keyword in the configuration file and returns whether the "+" option
        syntax is used.

        A "+" before the list of values denotes that the values are appended to
        the openssh defaults for the particular keyword.

        Returns True if the "+" is used, False if a line with the keyword was
        found but it doesn't use the "+" or None if such a line doesn't exist.

        Reasoning for the implementation:

        * The "+" means "added to the defaults".
        * The defaults depend on the particular openssh-server version and
          the parser doesn't know the version.
        * Therefore, it is infeasible to add the evaluation logic for "+"
          into `get_values()`.
        * Adding the logic into a combiner would mean a requirement that
          the combiner has a complete database of all defaults in all
          openssh-server version - infeasible again.
        * Not every keyword allows the use of "+" - it wouldn't make sense
          to parse "+" into `KeyValue` as it would make meaningless parsing
          for some options and meaningful for others. Building a database
          which options in which openssh-server versions support it or not
          would be infeasible.
        * The way chosen as the most sensible is this - `line_uses_plus()`
          used selectively by a rule for those options that support it, and
          it is up to the developer of such a rule to check it for those
          options manually.

        Parameters:
            keyword(str): Keyword to find
        """
        lines = self.get(keyword)
        if lines:
            found_line = lines[-1].line
            match = PLUS_PATTERN.match(found_line)
            return bool(match)
        else:
            return None

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


@parser(Specs.sshd_test_mode)
class SshdTestMode(Parser, dict):
    """
    This parser reads the output of "/usr/sbin/sshd -T" command.

    Sample output::

        port 22
        addressfamily any
        listenaddress [::]:22
        listenaddress 0.0.0.0:22
        usepam yes
        logingracetime 120
        x11displayoffset 10
        x11maxdisplays 1000
        maxauthtries 6
        ciphers aes256-gcm@openssh.com,chacha20-poly1305@openssh.com,aes256-ctr,aes128-gcm@openssh.com,aes128-ctr
        macs hmac-sha2-256-etm@openssh.com,hmac-sha1-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha2-256,hmac-sha1,umac-128@openssh.com,hmac-sha2-512

    Examples:
        >>> len(sshd_test_mode)
        10
        >>> sshd_test_mode.get("listenaddress")
        ['[::]:22', '0.0.0.0:22']
        >>> sshd_test_mode.get("ciphers")
        ['aes256-gcm@openssh.com,chacha20-poly1305@openssh.com,aes256-ctr,aes128-gcm@openssh.com,aes128-ctr']
    """
    def parse_content(self, content):
        result = {}
        for line in get_active_lines(content):
            key, value = line.split(" ", 1)
            if key in result:
                result[key].append(value)
            else:
                result[key] = [value]
        self.update(result)


@parser(Specs.sshd_config_d)
class SshDConfigD(SshDConfig):
    """
    Parsing for ``/etc/ssh/sshd_config.d/*.conf`` file.

    Typical content looks like::

        Include /etc/crypto-policies/back-ends/opensshserver.config

        SyslogFacility AUTHPRIV

        ChallengeResponseAuthentication no


    Examples:
        >>> sshd_config_d['Include']
        ['/etc/crypto-policies/back-ends/opensshserver.config']

    Properties:
        lines (list): List of `KeyValue` namedtupules for each line in
            the configuration file.
        keywords (set): Set of keywords present in the configuration
            file, each keyword has been converted to lowercase.
    """
    pass
