import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import dig
from insights.parsers.dig import Dig, DigDnssec, DigEdns, DigNoedns
from insights.tests import context_wrap

SIGNED_DNSSEC = """; <<>> DiG 9.11.1-P3-RedHat-9.11.1-2.P3.fc26 <<>> +dnssec nic.cz. SOA
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
;; MSG SIZE  rcvd: 189"""

NOT_SIGNED_DNSSEC = """; <<>> DiG 9.11.1-P3-RedHat-9.11.1-2.P3.fc26 <<>> +dnssec google.com. SOA
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 13253
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags: do; udp: 4096
;; QUESTION SECTION:
;google.com.                    IN      SOA

;; ANSWER SECTION:
google.com.             60      IN      SOA     ns1.google.com.
dns-admin.google.com. 173219439 900 900 1800 60

;; Query time: 46 msec
;; SERVER: 10.38.5.26#53(10.38.5.26)
;; WHEN: Tue Oct 24 14:28:20 CEST 2017
;; MSG SIZE  rcvd: 89"""

BAD_DNSSEC = """; <<>> DiG 9.11.1-P3-RedHat-9.11.1-2.P3.fc26 <<>> +dnssec google.com. SOA
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: REFUSED, id: 13253
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags: do; udp: 4096
;; QUESTION SECTION:
;google.com.                    IN      SOA

;; ANSWER SECTION:
google.com.             60      IN      SOA     ns1.google.com.
dns-admin.google.com. 173219439 900 900 1800 60

;; Query time: 46 msec
;; SERVER: 10.38.5.26#53(10.38.5.26)
;; WHEN: Tue Oct 24 14:28:20 CEST 2017
;; MSG SIZE  rcvd: 89"""

GOOD_EDNS = """; <<>> DiG 9.11.1-P3-RedHat-9.11.1-3.P3.fc26 <<>> +edns=0 . SOA
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
;; MSG SIZE  rcvd: 103"""

BAD_EDNS = """; <<>> DiG 9.11.1-P3-RedHat-9.11.1-3.P3.fc26 <<>> +edns=0 . SOA
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: SERVFAIL, id: 11158
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
;; MSG SIZE  rcvd: 103"""

GOOD_NOEDNS = """; <<>> DiG 9.11.1-P3-RedHat-9.11.1-3.P3.fc26 <<>> +noedns . SOA
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
;; MSG SIZE  rcvd: 92"""

BAD_NOEDNS = """; <<>> DiG 9.11.1-P3-RedHat-9.11.1-2.P3.fc26 <<>> +noedns
ewf-dwqfwqf-gdsa.com SOA
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NXDOMAIN, id: 30634
;; flags: qr rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 1, ADDITIONAL: 0

;; QUESTION SECTION:
;ewf-dwqfwqf-gdsa.com.          IN      SOA

;; AUTHORITY SECTION:
com.                    900     IN      SOA     a.gtld-servers.net.
nstld.verisign-grs.com. 1508851057 1800 900 604800 86400

;; Query time: 29 msec
;; SERVER: 10.38.5.26#53(10.38.5.26)
;; WHEN: Tue Oct 24 15:17:53 CEST 2017
;; MSG SIZE  rcvd: 111"""


def test_dig_no_data():
    with pytest.raises(SkipComponent):
        Dig(context_wrap(""), "")


def test_dig_dnssec():
    dig_dnssec = DigDnssec(context_wrap(SIGNED_DNSSEC))
    assert dig_dnssec.status == "NOERROR"
    assert dig_dnssec.has_signature

    dig_dnssec = DigDnssec(context_wrap(NOT_SIGNED_DNSSEC))
    assert dig_dnssec.status == "NOERROR"
    assert not dig_dnssec.has_signature

    dig_dnssec = DigDnssec(context_wrap(BAD_DNSSEC))
    assert dig_dnssec.status == "REFUSED"
    assert not dig_dnssec.has_signature


def test_dig_edns():
    dig_edns = DigEdns(context_wrap(GOOD_EDNS))
    assert dig_edns.status == "NOERROR"
    assert not dig_edns.has_signature

    dig_edns = DigEdns(context_wrap(BAD_EDNS))
    assert dig_edns.status == "SERVFAIL"
    assert not dig_edns.has_signature


def test_dig_noedns():
    dig_noedns = DigNoedns(context_wrap(GOOD_NOEDNS))
    assert dig_noedns.status == "NOERROR"
    assert not dig_noedns.has_signature

    dig_noedns = DigNoedns(context_wrap(BAD_NOEDNS))
    assert dig_noedns.status == "NXDOMAIN"
    assert not dig_noedns.has_signature


def test_doc_examples():
    env = {
        "dig_dnssec": DigDnssec(context_wrap(SIGNED_DNSSEC)),
        "dig_edns": DigEdns(context_wrap(GOOD_EDNS)),
        "dig_noedns": DigNoedns(context_wrap(GOOD_NOEDNS)),
    }
    failed, total = doctest.testmod(dig, globs=env)
    assert failed == 0
