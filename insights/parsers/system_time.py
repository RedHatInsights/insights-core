"""
System time configuration
=========================

This is a collection of parsers that all deal with the system's configuration
of its time setting resources.

"""

import re
from .. import Parser, parser, get_active_lines, CommandParser
from insights.specs import Specs


class NTPConfParser(Parser):
    """
    NTP and Chrony both use the same format for their configuration file -
    a series of keywords with optional values.  Some keywords can appear
    more than once, so all keyword values are stored as a list of strings.
    Keywords that have no value, like 'iburst' or 'rtcsync', are left as
    keys but have None as a value.

    Also provides the ``servers`` and ``peers`` properties as (sorted) lists
    of the found 'server' and 'peer' data (respectively).

    Sample Input::
        >>> ntp_conf_data = '''
        ... server 0.rhel.pool.ntp.org iburst
        ... server 1.rhel.pool.ntp.org iburst
        ... server 2.rhel.pool.ntp.org iburst
        ... server 3.rhel.pool.ntp.org iburst
        ... # Enable kernel RTC synchronization.
        ... rtcsync
        ... leapsecmode slew
        ... maxslewrate 1000
        ... smoothtime 400 0.001 leaponly
        ... tinker step 0.9
        ... '''

    Examples:

        >>> ntp = shared[NTP_conf]
        >>> 'rtcsync' in ntp.data # Single word options are present but None
        True
        >>> ntp.data['rtcsync'] # Not in dictionary if option not set
        None
        >>> len(ntp.data['server'])
        4
        >>> ntp.data['server'][0]
        '0.rhel.pool.ntp.org iburst'
        >>> ntp.servers[0] # same data as above
        '0.rhel.pool.ntp.org iburst'
        >>> ntp.data['maxslewrate']
        '1000'
        >>> ntp.get_last('rtcsync') # See above for fetching single-word options
        None
        >>> ntp.get_last('leapsecmode')
        'slew'
        >>> ntp.get_last('tinker', 'panic', 'none') # Use default value
        'none'
        >>> ntp.get_last('tinker', 'step', '1') # Use value set in file
        '0.9'
        >>> ntp.get_param('tinker', 'step') # Get list of all settings
        ['0.9']
    """
    def parse_content(self, content):
        data = {}
        for line in get_active_lines(content):
            if ' ' in line or '\t' in line:
                k, rest = line.split(None, 1)
                if k in data:
                    data[k].append(rest)
                else:
                    data[k] = [rest]
            else:
                data[line] = None
        self.data = data

        # Also set up some convenience access to lists of stuff:
        if 'server' in data:
            self.servers = sorted(data['server'])
        else:
            self.servers = []
        if 'peer' in data:
            self.peers = sorted(data['peer'])
        else:
            self.peers = []

    def get_param(self, keyword, param=None, default=None):
        """
        Get all the parameters for a given keyword, or default if keyword or
        parameter are not present in the configuration.

        This finds every declaration of the given parameter (which is the
        one which takes effect).  If no parameter is given, then the entire
        line is treated as the parameter.  There is always at least one
        element returned - the default, or

        Parameters:
            keyword(str): The keyword name, e.g. 'tinker' or 'driftfile'
            param(str): The parameter name, e.g. 'panic' or 'step'.  If not
                given, all the definitions of that keyword are given.
            default(str): The default (singular) value if the keyword or
                parameter is not found.  If not given, None is used.

        Returns:
            list: All the values of the given parameter, or an empty list if
            not found.
        """
        if not keyword or keyword not in self.data:
            return [default]
        # keyword in data - if no value, we store None, so return that in a list
        if self.data[keyword] is None:
            return [None]
        # If we're not searching for a particular parameter, just return all
        # the values for this keyword.
        if not param:
            return self.data[keyword]

        found = []
        for line in self.data[keyword]:
            # Line has already had keyword removed.
            words = line.strip().split()
            if len(words) > 1:
                # Line has param and value - check param:
                if words[0] == param:
                    found.append(words[1])
            else:
                found.append(words[0])
        if found == []:
            return [default]
        else:
            return found

    def get_last(self, keyword, param=None, default=None):
        """
        Get the parameters for a given keyword, or default if keyword or
        parameter are not present in the configuration.

        This finds the last declaration of the given parameter (which is the
        one which takes effect).  If no parameter is given, then the entire
        line is treated as the parameter and returned.

        Parameters:
            keyword(str): The keyword name, e.g. 'tinker' or 'driftfile'
            param(str): The parameter name, e.g. 'panic' or 'step'.  If not
                given, the last definition of that keyword is given.

        Returns:
            str or None: The value of the given parameter, or None if not
            found.
        """
        return self.get_param(keyword, param, default)[-1]


@parser(Specs.chrony_conf)
class ChronyConf(NTPConfParser):
    """
    A parser for analyzing the chrony service config file ``/etc/chrony.conf``

    Uses the ``NTPConfParser`` class defined in this module.
    """
    pass


@parser(Specs.ntp_conf)
class NTPConf(NTPConfParser):
    """
    A parser for analyzing the ntpd service config file ``/etc/ntp.conf``

    Uses the ``NTPConfParser`` class defined in this module.
    """
    pass


@parser(Specs.localtime)
class LocalTime(CommandParser):
    """
    A parser for working with the output of command: `file -L /etc/localtime`

    Sample Input::

        /etc/localtime: timezone data, version 2, 5 gmt time flags, 5 std time flags, no leap seconds, 69 transition times, 5 abbreviation chars

    Examples:

        >>> localtime = shared[LocalTime]
        >>> localtime.data['name']
        '/etc/localtime'
        >>> localtime.data['version']
        '2'
        >>> localtime.data['gmt_time_flag']
        '5'
        >>> localtime.data['leap_second']
        'no'
    """
    def parse_content(self, content):
        result = {}
        title = [
            'version',
            'gmt_time_flag',
            'std_time_flag',
            'leap_second',
            'transition_time',
            'abbreviation_char'
        ]
        for line in content:
            filename, info = line.strip().split(':', 1)
            result['name'] = filename.strip()
            info_list = info.split(', ')
            if len(info_list) == 7 and info_list[0].strip() == 'timezone data':
                # A bit of a hack - version field has the data second, all
                # other fields have the data first.
                for idx, k in enumerate(title):
                    if idx == 0:
                        result[k] = info_list[idx + 1].strip().split()[1]
                    else:
                        result[k] = info_list[idx + 1].strip().split()[0]
        self.data = result


@parser(Specs.ntptime)
class NtpTime(CommandParser):
    """
    A parser for working with the output of the ``ntptime``.

    This doesn't attempt to get much out of the output; useful things that
    it retrieves are:

    * ``ntp_gettime`` - the return code of the ``ntp_gettime()`` call.
    * ``ntp_adjtime`` - the return code of the ``ntp_adjtime()`` call.
    * ``status`` - the hexadecimal status code as a string.
    * ``flags`` - the flags in brackets after the status code.

    Sample Input::

        ntp_gettime() returns code 0 (OK)
          time dbbc595d.1adbd720  Thu, Oct 27 2016 18:45:49.104, (.104917550),
          maximum error 263240 us, estimated error 102 us, TAI offset 0
        ntp_adjtime() returns code 0 (OK)
          modes 0x0 (),
          offset 0.000 us, frequency 4.201 ppm, interval 1 s,
          maximum error 263240 us, estimated error 102 us,
          status 0x2011 (PLL,INS,NANO),
          time constant 2, precision 0.001 us, tolerance 500 ppm,

    Examples:

        >>> ntptime = shared[NtpTime]
        >>> ntptime.data['stats']
        '0x2011'
        >>> ntptime.data['ntp_gettime']
        '0'
        >>> ntptime.data['flags']
        ['PLL', 'INS', 'NANO']
        >>> ntptime.data['interval']  # Other values are integers or floats
        1
        >>> ntptime.data['precision']  # Note floats may not be exact
        0.001
        >>> ntptime.data['maximum error']
        263240

    """
    def parse_content(self, content):
        result = {}
        return_code_re = re.compile(r'(?P<func>ntp_(?:get|adj)time)\(\) returns code (?P<code>\d+) ')
        status_code_re = re.compile(r'status (?P<status>0x[0-9a-f]+) \((?P<flags>.*)\)')
        time_data_re = re.compile(r'time (?P<timecode>[0-9a-f]{8}\.[0-9a-f]{8}) +(?P<timestamp>\w{3}, \w{3} \d+ .*),')
        value_re = re.compile(r'(?P<keyword>[A-Za-z][A-Za-z ]+) (?P<value>\d+(?:\.\d+|x[0-9a-f]+)?) ?(?P<units>us|ppm|s|\(.*\))?')
        # Note that maximum and estimated error appear in both sections but
        # have the same value, so we don't bother to make them unique
        for line in content:
            # Check for function line
            match = return_code_re.search(line)
            if match:
                function = match.group('func')
                result[function] = match.group('code')
                continue

            # Check for status line specially
            match = status_code_re.search(line)
            if match:
                result['status'] = match.group('status')
                result['flags'] = match.group('flags').split(',')
                continue

            # Check for time data specially
            match = time_data_re.search(line)
            if match:
                # Get timecode and timestamp in one go
                result.update(match.groupdict())
                continue

            # Otherwise, try to read comma-separated key-value groups
            for match in value_re.finditer(line):
                value = match.group('value')
                if '.' in value:
                    vnum = float(value)
                elif 'x' in value:
                    vnum = int(value, 16)
                else:
                    vnum = int(value)
                result[match.group('keyword')] = vnum

        self.data = result
