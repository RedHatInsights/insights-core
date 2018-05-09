"""
NTP sources - remote clock info from ``ntpq`` and ``chronyc``
=============================================================

The parsers here provide information about the time sources used by
``ntpd`` and ``chronyd``.  These are gathered from the output of the
``ntpq -pn`` and ``chronyc sources`` commands respectively.

There is also a parser for parsing the output of ``ntpq -c 'rv 0 leap'``
command to give leap second status.

Parsers in this module are:

ChronycSources - command ``/usr/bin/chronyc sources``
-----------------------------------------------------

NtpqLeap - command ``/usr/sbin/ntpq -c 'rv 0 leap'``
----------------------------------------------------

NtpqPn - command ``/usr/sbin/ntpq -pn``
---------------------------------------


"""

import re
from .. import parser, CommandParser
from insights.core.dr import SkipComponent
from insights.specs import Specs


@parser(Specs.chronyc_sources)
class ChronycSources(CommandParser):
    """
    Chronyc Sources parser

    Parses the list of NTP time sources in use by ``chronyd``.  So far only
    the source IP address and the mode and the state flags are retrieved.

    Sample input::

        210 Number of sources = 6
        MS Name/IP address         Stratum Poll Reach LastRx Last sample
        ===============================================================================
        ^- 10.20.30.40                   2   9   377    95  -1345us[-1345us] +/-   87ms
        ^- 10.56.72.8                    2  10   377   949  -3449us[-3483us] +/-  120ms
        ^* 10.64.108.95                  2  10   377   371    -91us[ -128us] +/-   30ms
        ^- 10.8.205.17                   2   8   377    27  +7161us[+7161us] +/-   52ms

    Examples:

        >>> sources = shared[ChronycSources].data
        >>> len(sources)
        4
        >>> sources[0]['source']
        '10.20.30.40'
        >>> sources[0]['mode']
        '^'
        >>> sources[0]['state']
        '-'
    """

    def parse_content(self, content):
        """
        Get source, mode and state for chrony
        """
        self.data = []
        for row in content[3:]:
            if row.strip():
                values = row.split(" ", 2)
                self.data.append({"source": values[1], "mode": values[0][0], "state": values[0][1]})


@parser(Specs.ntpq_leap)
class NtpqLeap(CommandParser):
    """
    Converts the output of ``ntpq -c 'rv 0 leap'`` into a dictionary in the
    ``data`` property, and sets the ``leap`` property to the value of the
    'leap' key if found.

    Sample input::

        leap=00

    Examples:

        >>> print shared[NtpqLeap].leap  # same data
        '00'
    """

    def parse_content(self, content):
        if "Connection refused" in content[0]:
            raise SkipComponent("NTP service is down and connection refused")
        self.data = {}
        for line in content:
            m = re.search(r'leap=(\d*)', line)
            if m:
                self.data["leap"] = m.group(1)

    @property
    def leap(self):
        return self.data.get('leap')


@parser(Specs.ntpq_pn)
class NtpqPn(CommandParser):
    """
    Get source and flag for each NTP time source from the output of
    ``/usr/sbin/ntpq -pn``.

    Currently, this only captures the source IP address and the 'flag'
    character in the first column at this stage.  Therefore it will need
    to be extended should you wish to determine the stratum, polling rate
    or other properties of the source.

    Sample input::

             remote           refid      st t when poll reach   delay   offset  jitter
        ==============================================================================
        +10.20.30.40     192.231.203.132  3 u  638 1024  377    0.242    2.461   1.886
        *2001:388:608c:8 .GPS.            1 u  371 1024  377   29.323    1.939   1.312
        -2001:44b8:1::1  216.218.254.202  2 u  396 1024  377   37.869   -3.340   6.458
        +150.203.1.10    202.6.131.118    2 u  509 1024  377   20.135    0.800   3.260

    Examples:

        >>> sources = shared[NtpqPn].data
        >>> len(sources)
        4
        >>> sources[0]
        {'flag': '*', 'source', '10.20.30.40'}
    """

    def parse_content(self, content):
        if "Connection refused" in content[0]:
            raise SkipComponent("NTP service is down and connection refused")
        self.data = []
        for row in content[2:]:
            if row.strip():
                values = row.split(" ", 2)
                if row.startswith(" "):
                    self.data.append({"source": values[1], "flag": " "})
                else:
                    self.data.append({"source": values[0][1:], "flag": values[0][0]})
