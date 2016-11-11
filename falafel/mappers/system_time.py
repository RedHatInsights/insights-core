import re
from .. import Mapper, mapper, get_active_lines


@mapper("chrony.conf")
class ChronyConf(Mapper):
    """
    A mapper for analyzing the chrony service config file /etc/chrony.conf
    """
    def parse_content(self, content):
        """
        Returns a dict object contains all settings in /etc/chrony.conf.

        Sample Input:
            server 0.rhel.pool.ntp.org iburst
            server 1.rhel.pool.ntp.org iburst
            server 2.rhel.pool.ntp.org iburst
            server 3.rhel.pool.ntp.org iburst
            # Enable kernel RTC synchronization.
            rtcsync
            leapsecmode slew
            maxslewrate 1000
            smoothtime 400 0.001 leaponly

        Sample Output:

        .. code-block:: python

            {'server': ["0.rhel.pool.ntp.org iburst",
                "0.rhel.pool.ntp.org iburst",
                "2.rhel.pool.ntp.org iburst",
                "3.rhel.pool.ntp.org iburst"]
            'rtcsync': None,
            'leapsecmode': ['slew]',
            'maxslewrate': ['1000]',
            'smoothtime': ['400 0.001 leaponly']
            }
        """
        result = {}
        for line in get_active_lines(content):
            if ' ' in line:
                k, rest = line.split(None, 1)
                if k in result:
                    result[k].append(rest)
                else:
                    result[k] = [rest]
            else:
                result[line] = None
        self.data = result


@mapper("localtime")
class LocalTime(Mapper):
    """
    A mapper for working with the output of command: file -L /etc/localtime
    """
    def parse_content(self, content):
        """
        Stores all interesting data from the content.

        Sample Input:
          /etc/localtime: timezone data, version 2, 5 gmt time flags, \
          5 std time flags, no leap seconds, 69 transition times, 5 abbreviation chars

        Sample Output:

        .. code-block:: python

             {
              'name': '/etc/localtime',
              'leap_second': 'no',
              'transition_time': '69',
              'version': '2',
              'std_time_flag': '5',
              'abbreviation_char': '5',
              'gmt_time_flag': '5'
            }
        """
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
            if len(info_list) == 7:
                if info_list[0].strip() == 'timezone data':
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
    A mapper for working with the output of command: ntptime
    """
    def parse_content(self, content):
        """
        Grab important return values from the content.

        Sample Input:
          ntp_gettime() returns code 0 (OK)
            time dbbc595d.1adbd720  Thu, Oct 27 2016 18:45:49.104, (.104917550),
            maximum error 263240 us, estimated error 102 us, TAI offset 0
          ntp_adjtime() returns code 0 (OK)
            modes 0x0 (),
            offset 0.000 us, frequency 4.201 ppm, interval 1 s,
            maximum error 263240 us, estimated error 102 us,
            status 0x2011 (PLL,INS,NANO),
            time constant 2, precision 0.001 us, tolerance 500 ppm,

        Sample Output:

        .. code-block:: python

            {
              'status': '0x2011',
              'flags': ['PLL', 'INS', 'NANO'],
              'ntp_adjtime': '0',
              'ntp_gettime': '0'
            }
        """
        funcname = [
            'ntp_gettime',
            'ntp_adjtime'
        ]
        result = {}
        for line in content:
            for func in funcname:
                if func in line:
                    reg = re.compile(r'returns code (\d+) ')
                    g = reg.search(line)
                    if g and g.lastindex == 1:
                        result[func] = g.group(1)
            if "status " in line:
                frags = line.split()
                if len(frags) == 3:
                    result['status'] = frags[1]
                    reg = re.compile(r'\((.*)\)')
                    g = reg.search(frags[2])
                    if g and g.lastindex == 1:
                        result['flags'] = g.group(1).split(',')
        self.data = result


@mapper("sysconfig_chronyd")
class ChronydService(Mapper):
    """
    A mapper for analyzing the chronyd service config file in /etc/sysconfig
    directory
    """
    def parse_content(self, content):
        """
        Returns a dict object contains all settings in /etc/sysconfig/chronyd.

        Sample Input:
          OPTIONS="-d"
          #HIDE="me"

        Sample Output:

        .. code-block:: python

            {'OPTIONS': '"-d"'}
        """
        result = {}
        for line in get_active_lines(content):
            if '=' in line:
                k, rest = line.split('=', 1)
                result[k.strip()] = rest.strip()
        self.data = result


@mapper("sysconfig_ntpd")
class NTPDService(Mapper):
    """
    A mapper for analyzing the ntpd service config file in /etc/sysconfig
    directory
    """
    def parse_content(self, content):
        """
        Returns a dict object contains all settings in /etc/sysconfig/ntpd.

        Sample Input:
          OPTIONS="-x -g"
          #HIDE="me"

        Sample Output:

        .. code-block:: python

            {'OPTIONS': '"-x -g"'}
        """
        result = {}
        for line in get_active_lines(content):
            if '=' in line:
                k, rest = line.split('=', 1)
                result[k.strip()] = rest.strip()
        self.data = result
