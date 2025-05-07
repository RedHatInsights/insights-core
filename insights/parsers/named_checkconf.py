"""
NamedCheckconf parser - command ``named-checkconf -p``
======================================================

Named-checkconf is a syntax checking tool for named configuration file.
Named is a name server used by BIND.
"""

from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.core.filters import add_filter
from insights.specs import Specs

OPTIONS_ONE_LINE_NAMES = ['max-cache-size', 'cleaning-interval', 'dnssec-enable']
OPTIONS_MUL_LINES_NAMES = ['disable-algorithms', 'disable-ds-digests']

add_filter(Specs.named_checkconf_p, '};')


@parser(Specs.named_checkconf_p)
class NamedCheckconf(CommandParser):
    """
    Class for parsing the ``named-checkconf -p`` command. But the output is filtered.

    Attributes:
        is_dnssec_disabled (bool): True, if dnssec is not enabled, False otherwise.
        dnssec_line (string): The line which disabled dnssec, if it is not enabled, None otherwise.
        disable_algorithms (dict): Dictionary where the key is a domain and
                                   the value is a list of all algorithms associated with it.
        disable_ds_digests (dict): Dictionary where the key is a domain and
                                   the value is a list of all digests associated with it.
        options (dict): A dictionary contains all the options. The key is the option name, the value is
                                   the value but removed quote and semi-colon. However if the value of
                                   the option spans multiple lines, the value is a list.

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
        >>> named_checkconf.options['disable-algorithms']
        {'.': ['RSAMD5', 'DSA']}
        >>> named_checkconf.options['disable-ds-digests']
        {'.': ['GOST']}
        >>> named_checkconf.options['dnssec-enable']
        'yes'
    """

    def __init__(self, context):
        self.is_dnssec_disabled = False  # dnssec is enabled by default
        self.dnssec_line = None
        self.options = {}
        super(NamedCheckconf, self).__init__(context)

    def parse_content(self, content):
        if not content:
            raise SkipComponent('No content.')

        option_values = None
        for line in content:
            line = line.strip()
            if not line:
                continue
            items = line.split()
            if items[0] in OPTIONS_ONE_LINE_NAMES:
                value = ' '.join(items[1:]).strip('\'";')
                self.options[items[0]] = value
                # to be compatible with previous code
                # it will be deleted later when there is no reference with it
                # plese use self.options to get data now.
                if items[0] == 'dnssec-enable' and value == 'no':
                    self.is_dnssec_disabled = True
                    self.dnssec_line = line
            elif items[0] in OPTIONS_MUL_LINES_NAMES:
                name_value = ' '.join(items[1:]).strip('\'"{ ')
                self.options[items[0]] = {name_value: []}
                option_values = self.options[items[0]][name_value]
            elif option_values is not None and line != '};':
                option_values.append(line.strip('\'"; '))
            elif option_values is not None and line == '};':
                option_values = None

        # to be compatible with previous code
        # it will be deleted later when there is no reference with it
        # plese use self.options to get data now.
        self.disable_algorithms = self.options['disable-algorithms'] if 'disable-algorithms' in self.options else {}
        self.disable_ds_digests = self.options['disable-ds-digests'] if 'disable-ds-digests' in self.options else {}
