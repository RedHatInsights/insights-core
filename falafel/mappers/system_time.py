"""
System time configuration
=========================

This is a collection of mappers that all deal with the system's configuration
of its time setting resources.
"""

import re
from .. import Mapper, mapper, get_active_lines, SysconfigOptions


class NTPConfMapper(Mapper):
    """
    NTP and Chrony both use the same format for their configuration file -
    a series of keywords with optional values.  Some keywords can appear
    more than once, so all keyword values are stored as a list of strings.
    Keywords that have no value, like 'iburst' or 'rtcsync', are left as
    keys but have None as a value.

    Also provides the ``servers`` and ``peers`` properties as (sorted) lists
    of the found 'server' and 'peer' data (respectively).

    Sample Input::

        server 0.rhel.pool.ntp.org iburst
        server 1.rhel.pool.ntp.org iburst
        server 2.rhel.pool.ntp.org iburst
        server 3.rhel.pool.ntp.org iburst
        # Enable kernel RTC synchronization.
        rtcsync
        leapsecmode slew
        maxslewrate 1000
        smoothtime 400 0.001 leaponly

    Examples:

        >>> ntp = shared[NTP_conf]
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
    """
    def parse_content(self, content):
        data = {}
        for line in get_active_lines(content):
            if ' ' in line:
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


@mapper("chrony.conf")
class ChronyConf(NTPConfMapper):
    """
    A mapper for analyzing the chrony service config file /etc/chrony.conf

    Uses the ``NTPConfMapper`` class defined in this module.
    """
    pass


@mapper("ntp.conf")
class NTP_conf(NTPConfMapper):
    """
    A mapper for analyzing the ntpd service config file /etc/ntp.conf

    Uses the ``NTPConfMapper`` class defined in this module.
    """
    pass


@mapper("localtime")
class LocalTime(Mapper):
    """
    A mapper for working with the output of command: `file -L /etc/localtime`

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
            info_list = info.split(',')
            if len(info_list) == 7 and info_list[0].strip() == 'timezone data':
                idx = 1
                for k in title:
                    if idx == 1:
                        result[k] = info_list[idx].strip().split()[1]
                    else:
                        result[k] = info_list[idx].strip().split()[0]
                    idx = idx + 1
        self.data = result


@mapper("ntptime")
class NtpTime(Mapper):
    """
    A mapper for working with the output of the ``ntptime`` command.

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

    """
    def parse_content(self, content):
        funcname = [
            'ntp_gettime',
            'ntp_adjtime'
        ]
        result = {}
        return_code_re = re.compile(r'returns code (\d+) ')
        status_code_re = re.compile(r'\((.*)\)')
        for line in content:
            for func in funcname:
                if func in line:
                    g = return_code_re.search(line)
                    if g and g.lastindex == 1:
                        result[func] = g.group(1)
            if "status " in line:
                frags = line.split()
                if len(frags) == 3:
                    result['status'] = frags[1]
                    g = status_code_re.search(frags[2])
                    if g and g.lastindex == 1:
                        result['flags'] = g.group(1).split(',')
        self.data = result


@mapper("sysconfig_chronyd")
class ChronydService(SysconfigOptions):
    """
    A mapper for analyzing the ``chronyd`` service config file in the
    ``/etc/sysconfig`` directory.

    Sample Input::

      OPTIONS="-d"
      #HIDE="me"

    Examples:

        >>> service_opts = shared[ChronydService]
        >>> 'OPTIONS' in service_opts.data
        True
        >>> 'HIDE' in service_opts.data
        False
        >>> service_opts.data['OPTIONS']
        '"-d"'

    """
    pass


@mapper("sysconfig_ntpd")
class NTPDService(SysconfigOptions):
    """
    A mapper for analyzing the ``ntpd`` service config file in the
    ``/etc/sysconfig`` directory

    Sample Input::

      OPTIONS="-x -g"
      #HIDE="me"

    Examples:

        >>> service_opts = shared[NTPDService]
        >>> 'OPTIONS' in service_opts.data
        True
        >>> 'HIDE' in service_opts.data
        False
        >>> service_opts.data['OPTIONS']
        '"-x -g"'
    """
    pass
