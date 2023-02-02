"""
NamedCheckconf parser - command ``named-checkconf -p``
======================================================

Named-checkconf is a syntax checking tool for named configuration file.
Named is a name server used by BIND.
"""

import re

from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs

# regex for matching 'dnssec-enable no'
DNSSEC_DISABLED = re.compile(r'dnssec-enable\s+no;')
# regex for matching 'disable-algorithms' section
DISABLE_ALGORITHMS = re.compile(r'disable-algorithms[^}]*};')
# regex for matching 'disable-ds-digests' section
DISABLE_DS_DIGESTS = re.compile(r'disable-ds-digests[^}]*};')
# regex for matching values in single or double quotation marks
INNER_VALLUES = re.compile(r'(?:\"|\')(.*)(?:\"|\')')


@parser(Specs.named_checkconf_p)
class NamedCheckconf(CommandParser):
    """
    Class for parsing the ``named-checkconf -p`` command.

    Attributes:
        is_dnssec_disabled (bool): True, if dnssec is not enabled, False otherwise.
        dnssec_line (string): The line which disabled dnssec, if it is not enabled, None otherwise.
        disable_algorithms (dict): Dictionary where the key is a domain and
                                   the value is a list of all algorithms associated with it.
        disable_ds_digests (dict): Dictionary where the key is a domain and
                                   the value is a list of all digests associated with it.

    Raises:
        SkipComponent: When content is empty or cannot be parsed.

    Sample output of this command is::

        logging {
            channel "default_debug" {
                file "data/named.run";
                severity dynamic;
            };
        };
        options {
            directory "/var/named";
            dump-file "/var/named/data/cache_dump.db";
            listen-on port 53 {
                127.0.0.1/32;
            };
            listen-on-v6 port 53 {
                ::1/128;
            };
            managed-keys-directory "/var/named/dynamic";
            memstatistics-file "/var/named/data/named_mem_stats.txt";
            pid-file "/run/named/named.pid";
            recursing-file "/var/named/data/named.recursing";
            secroots-file "/var/named/data/named.secroots";
            session-keyfile "/run/named/session.key";
            statistics-file "/var/named/data/named_stats.txt";
            disable-algorithms "." {
                "RSAMD5";
                "DSA";
            };
            disable-ds-digests "." {
                "GOST";
            };
            dnssec-enable yes;
            dnssec-validation yes;
            recursion yes;
            allow-query {
                "localhost";
            };
        };
        managed-keys {
            "." initial-key 257 3 8 "AwEAAagAIKlVZrpC6Ia7gEzahOR+9W29euxhJhVVLOyQbSEW0O8gcCjF
                        FVQUTf6v58fLjwBd0YI0EzrAcQqBGCzh/RStIoO8g0NfnfL2MTJRkxoX
                        bfDaUeVPQuYEhg37NZWAJQ9VnMVDxP/VHL496M/QZxkjf5/Efucp2gaD
                        X6RS6CXpoY68LsvPVjR0ZSwzz1apAzvN9dlzEheX7ICJBBtuA6G3LQpz
                        W5hOA2hzCTMjJPJ8LbqF6dsV6DoBQzgul0sGIcGOYl7OyQdXfZ57relS
                        Qageu+ipAdTTJ25AsRTAoub8ONGcLmqrAmRLKBP1dfwhYB4N7knNnulq
                        QxA+Uk1ihz0=";
            "." initial-key 257 3 8 "AwEAAaz/tAm8yTn4Mfeh5eyI96WSVexTBAvkMgJzkKTOiW1vkIbzxeF3
                        +/4RgWOq7HrxRixHlFlExOLAJr5emLvN7SWXgnLh4+B5xQlNVz8Og8kv
                        ArMtNROxVQuCaSnIDdD5LKyWbRd2n9WGe2R8PzgCmr3EgVLrjyBxWezF
                        0jLHwVN8efS3rCj/EWgvIWgb9tarpVUDK/b58Da+sqqls3eNbuv7pr+e
                        oZG+SrDK6nWeL3c6H5Apxz7LjVc1uTIdsIXxuOLYA4/ilBmSVIzuDWfd
                        RUfhHdY6+cn8HFRm+2hM8AnXGXws9555KrUB5qihylGa8subX2Nn6UwN
                        R1AkUTV74bU=";
        };
        zone "." IN {
            type hint;
            file "named.ca";
        };
        zone "localhost.localdomain" IN {
            type master;
            file "named.localhost";
            allow-update {
                "none";
            };
        };
        zone "localhost" IN {
            type master;
            file "named.localhost";
            allow-update {
                "none";
            };
        };
        zone "1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.ip6.arpa" IN {
            type master;
            file "named.loopback";
            allow-update {
                "none";
            };
        };
        zone "1.0.0.127.in-addr.arpa" IN {
            type master;
            file "named.loopback";
            allow-update {
                "none";
            };
        };
        zone "0.in-addr.arpa" IN {
            type master;
            file "named.empty";
            allow-update {
                "none";
            };
        };

    Examples:
        >>> type(named_checkconf)
        <class 'insights.parsers.named_checkconf.NamedCheckconf'>
        >>> named_checkconf.is_dnssec_disabled
        False
        >>> named_checkconf.dnssec_line is None
        True
        >>> named_checkconf.disable_algorithms
        {'.': ['RSAMD5', 'DSA']}
        >>> named_checkconf.disable_ds_digests
        {'.': ['GOST']}
    """

    def __init__(self, context):
        self.is_dnssec_disabled = False  # dnssec is enabled by default
        self.dnssec_line = None
        self.disable_algorithms = {}
        self.disable_ds_digests = {}
        super(NamedCheckconf, self).__init__(context)

    def parse_content(self, content):
        if not content:
            raise SkipComponent('No content.')

        full_result = '\n'.join(content)

        match_dnssec = DNSSEC_DISABLED.search(full_result)
        if match_dnssec:
            self.is_dnssec_disabled = True
            self.dnssec_line = match_dnssec.group(0)

        self.disable_algorithms = self.retrieve_disabled(DISABLE_ALGORITHMS, full_result)
        self.disable_ds_digests = self.retrieve_disabled(DISABLE_DS_DIGESTS, full_result)

    def retrieve_disabled(self, section_regex, source):
        """
        Parses 'disable-algorithms' or 'disable_ds_digests' section into a dictionary,
        where the key is a domain and the value is a list of all algorithms/digests associated with it.

        Attributes:
            section_regex (string): The regular expression for a given section.
            source (string): The source in which a given section is searched for.
        """
        dict_of_sections = dict()
        for match_entry in section_regex.finditer(source):
            entry = match_entry.group(0)
            # collects all values in quotation marks for given section
            entry_values = [match_value.group(1) for match_value in INNER_VALLUES.finditer(entry)]
            dict_of_sections[entry_values[0]] = entry_values[1:]

        return dict_of_sections
