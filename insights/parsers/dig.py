"""
Domain information groper (Dig) parsers
=======================================

Parsers included in this module are:

DigDnssec - command ``/usr/bin/dig +dnssec . SOA``
--------------------------------------------------
DigEdns - command ``/usr/bin/dig +edns=0 . SOA``
------------------------------------------------
DigNoedns - command ``/usr/bin/dig +noedns . SOA``
--------------------------------------------------
"""
import re

from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


HEADER_TEMPLATE = re.compile(r';; ->>HEADER<<-.*status: (\S+),')
RRSIG_TEMPLATE = re.compile(r'RRSIG')


class Dig(CommandParser):
    """
    Base class for classes using ``dig`` command.

    Attributes:
        status (string): Determines if the lookup succeeded.
        has_signature (bool): True, if signature is present.
        command (string): Specific ``dig`` command used.

    Raises:
        SkipComponent: When content is empty or cannot be parsed.
    """
    def __init__(self, context, command):
        self.status = None
        self.has_signature = False
        self.command = command
        super(Dig, self).__init__(context)

    def parse_content(self, content):
        if not content:
            raise SkipComponent('No content.')

        for line in content:
            match = HEADER_TEMPLATE.search(line)
            if match:
                self.status = match.group(1)
            if RRSIG_TEMPLATE.search(line):
                self.has_signature = True


@parser(Specs.dig_dnssec)
class DigDnssec(Dig):
    """
    Class for parsing ``/usr/bin/dig +dnssec . SOA`` command.

    Sample output of this command is::

        ; <<>> DiG 9.11.1-P3-RedHat-9.11.1-2.P3.fc26 <<>> +dnssec nic.cz. SOA
        ;; global options: +cmd
        ;; Got answer:
        ;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 58794
        ;; flags: qr rd ra; QUERY: 1, ANSWER: 2, AUTHORITY: 0, ADDITIONAL: 1

        ;; OPT PSEUDOSECTION:
        ; EDNS: version: 0, flags: do; udp: 4096
        ;; QUESTION SECTION:
        ;nic.cz.                                IN      SOA

        ;; ANSWER SECTION:
        nic.cz.                 278     IN      SOA     a.ns.nic.cz.
        hostmaster.nic.cz. 1508686803 10800 3600 1209600 7200
        nic.cz.                 278     IN      RRSIG   SOA 13 2 1800
        20171105143612 20171022144003 41758 nic.cz.
        hq3rr8dASRlucMJxu2QZnX6MVaMYsKhmGGxBOwpkeUrGjfo6clzG6MZN
        2Jy78fWYC/uwyIsI3nZMUKv573eCWg==

        ;; Query time: 22 msec
        ;; SERVER: 10.38.5.26#53(10.38.5.26)
        ;; WHEN: Tue Oct 24 14:28:56 CEST 2017
        ;; MSG SIZE  rcvd: 189

    Examples:
        >>> dig_dnssec.status
        'NOERROR'
        >>> dig_dnssec.has_signature
        True
        >>> dig_dnssec.command
        '/usr/bin/dig +dnssec . SOA'
    """
    def __init__(self, context):
        super(DigDnssec, self).__init__(context, '/usr/bin/dig +dnssec . SOA')


@parser(Specs.dig_edns)
class DigEdns(Dig):
    """
    Class for parsing ``/usr/bin/dig +edns=0 . SOA`` command.

    Sample output of this command is::

        ; <<>> DiG 9.11.1-P3-RedHat-9.11.1-3.P3.fc26 <<>> +edns=0 . SOA
        ;; global options: +cmd
        ;; Got answer:
        ;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 11158
        ;; flags: qr rd ra ad; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

        ;; OPT PSEUDOSECTION:
        ; EDNS: version: 0, flags:; udp: 4096
        ;; QUESTION SECTION:
        ;.				IN	SOA

        ;; ANSWER SECTION:
        .			19766	IN	SOA	a.root-servers.net. nstld.verisign-grs.com. 2017120600 1800 900 604800 86400

        ;; Query time: 22 msec
        ;; SERVER: 10.38.5.26#53(10.38.5.26)
        ;; WHEN: Thu Dec 07 09:38:33 CET 2017
        ;; MSG SIZE  rcvd: 103

    Examples:
        >>> dig_edns.status
        'NOERROR'
        >>> dig_edns.has_signature
        False
        >>> dig_edns.command
        '/usr/bin/dig +edns=0 . SOA'
    """
    def __init__(self, context):
        super(DigEdns, self).__init__(context, '/usr/bin/dig +edns=0 . SOA')


@parser(Specs.dig_noedns)
class DigNoedns(Dig):
    """
    Class for parsing ``/usr/bin/dig +noedns . SOA`` command.

    Sample output of this command is::

        ; <<>> DiG 9.11.1-P3-RedHat-9.11.1-3.P3.fc26 <<>> +noedns . SOA
        ;; global options: +cmd
        ;; Got answer:
        ;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 47135
        ;; flags: qr rd ra ad; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0

        ;; QUESTION SECTION:
        ;.				IN	SOA

        ;; ANSWER SECTION:
        .			20195	IN	SOA	a.root-servers.net. nstld.verisign-grs.com. 2017120600 1800 900 604800 86400

        ;; Query time: 22 msec
        ;; SERVER: 10.38.5.26#53(10.38.5.26)
        ;; WHEN: Thu Dec 07 09:31:24 CET 2017
        ;; MSG SIZE  rcvd: 92

    Examples:
        >>> dig_noedns.status
        'NOERROR'
        >>> dig_noedns.has_signature
        False
        >>> dig_noedns.command
        '/usr/bin/dig +noedns . SOA'
    """
    def __init__(self, context):
        super(DigNoedns, self).__init__(context, '/usr/bin/dig +noedns . SOA')
