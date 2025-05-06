"""
Clean Specs (files/commands)
============================

The following modules are provided in the Cleaner and can be applied to the
specs during collection according to the user configuration and specs setting.

- Redaction (patterns redaction)
  This is a must-be-done operation to all the collected specs.  A `no_redact`
  option is available to specs, if it's surely contains non-security
  information, e.g. the `machine-id` spec.

- Filtering
  Filter lines as per the allow list got from the `filters.yaml`.  The
  `filtering` can only be applied when `allowlist` is available (not None) for
  the spec.

- Obfuscation (IPv4, [IPv6], Hostname, MAC, Password, Keywords)
  Obfuscate lines in spec content according to the user configuration and
  specs requirement.  The `no_obfuscate` can be used to exclude obfuscation
  target from the obfuscation.  Currently, the supported obfuscation target
  are:
  * hostname
  * ipv4
  * ipv6
  * keyword
  * mac
  * password
"""

import logging
import json
import os
import six

from insights.cleaner.filters import AllowFilter
from insights.cleaner.hostname import Hostname
from insights.cleaner.ip import IPv4, IPv6
from insights.cleaner.keyword import Keyword

from insights.cleaner.mac import Mac
from insights.cleaner.password import Password
from insights.cleaner.pattern import Pattern
from insights.cleaner.utilities import write_report
from insights.util.hostname import determine_hostname
from insights.util.posix_regex import replace_posix

logger = logging.getLogger(__name__)
MAX_LINE_LENGTH = 1048576  # 1MB
DEFAULT_OBFUSCATIONS = {
    'hostname',
    'ipv4',
    'ipv6',
    'keyword',
    'mac',
    'password',
}


class Cleaner(object):
    """
    Class to clean the content of Specs according to the user configuration and
    spec setting.
    """

    def __init__(self, config, rm_conf, fqdn=None):
        self.report_dir = '/tmp'  # FIXME
        self.rhsm_facts_file = getattr(
            config, 'rhsm_facts_file', os.path.join(self.report_dir, 'insights-client.facts')
        )
        # Handle User Configuration
        rm_conf = rm_conf or {}
        exclude = rm_conf.get('patterns', [])
        regex = False
        if isinstance(exclude, dict) and exclude.get('regex'):
            exclude = [r'%s' % replace_posix(i) for i in exclude['regex']]
            regex = True
        # - Pattern Redaction and allow-list Filtering
        self.redact = {
            'pattern': Pattern(exclude, regex) if exclude else None,
            'allow_filter': AllowFilter(),
        }
        # - Keyword and Password Replacement
        #   They Do NOT depend on "obfuscation_list"
        keywords = rm_conf.get('keywords')
        self.obfuscate = {
            'keyword': Keyword(keywords) if keywords else None,
            'password': Password(),
        }

        self.fqdn = fqdn if fqdn else determine_hostname()
        obfs = config.obfuscation_list if config else None
        if config and obfs:
            # - IPv4 obfuscation
            self.obfuscate.update(ipv4=IPv4()) if 'ipv4' in obfs else None
            # - IPv6 obfuscation
            self.obfuscate.update(ipv6=IPv6()) if 'ipv6' in obfs else None
            # - Hostname obfuscation
            self.obfuscate.update(hostname=Hostname(self.fqdn)) if 'hostname' in obfs else None
            # - MAC obfuscation
            self.obfuscate.update(mac=Mac()) if 'mac' in obfs else None

    def clean_content(self, lines, no_obfuscate=None, no_redact=False, allowlist=None, width=False):
        """
        Clean lines one by one according to the configuration.

        For some extra large files, e.g. logs, we want to keep the bottom
        part of them.  So the lines are processed in reverse order.  But the
        processed result is returned in the original order.
        """

        def _clean_line(line):
            if len(line) > MAX_LINE_LENGTH:
                # Keep the first MAX_LINE_LENGTH chars only (it rarely happens)
                line = line[:MAX_LINE_LENGTH]
                logger.debug('Extra-long line is truncated ...')

            for parser, kwargs in parsers:
                line = parser.parse_line(line, **kwargs)
            return line

        # List of parsers to be applied with Order
        parsers = list()
        # 1. Redact when NO "no_redact=True" is set
        if self.redact['pattern'] and not no_redact:
            parsers.append((self.redact['pattern'], {})) if not no_redact else None
        # 2. Filter as per allowlist got from add_filter  # copy it to avoid write back
        (
            parsers.append((self.redact['allow_filter'], {'allowlist': dict(allowlist)}))
            if allowlist is not None
            else None
        )
        # 3. Obfuscation entries
        # - Hostname
        # - IPv4
        # - IPv6
        # - Keyword
        # - Mac
        # - Password
        for obf in set(self.obfuscate.keys()) - set(no_obfuscate or []):
            if self.obfuscate[obf]:
                parsers.append((self.obfuscate[obf], {'width': width}))

        # handle single string
        if not isinstance(lines, list):
            return _clean_line(lines)

        result = []
        # process lines in reverse order
        for idx in range(len(lines) - 1, -1, -1):
            line = _clean_line(lines[idx])
            result.append(line) if line is not None else None
        if result and any(l for l in result):
            # When some lines Truthy, return them in right order
            result.reverse()
            return result
        # All lines blank
        return []

    def clean_file(self, _file, no_obfuscate=None, no_redact=False, allowlist=None):
        """
        Clean a file according to the configuration, the file will be updated
        directly with the cleaned content.
        """
        logger.debug('Cleaning %s ...' % _file)

        if os.path.exists(_file) and not os.path.islink(_file):
            # Process the file
            raw_data = content = None
            try:
                with open(_file, 'r') as fh:
                    raw_data = fh.readlines()
                    content = self.clean_content(
                        raw_data,
                        no_obfuscate=no_obfuscate,
                        no_redact=no_redact,
                        allowlist=allowlist,
                        width=_file.endswith("netstat_-neopa"),
                    )
            except Exception as e:  # pragma: no cover
                logger.warning(e)
                raise Exception("Error: Cannot Open File for Cleaning: %s" % _file)
            # Store it
            try:
                if raw_data:
                    if content:
                        with open(_file, 'wb') as fh:
                            for line in content:
                                fh.write(line.encode('utf-8') if six.PY3 else line)
                    else:
                        # Remove Empty file
                        logger.debug('Removing %s, as it\'s empty after cleaning' % _file)
                        os.remove(_file)
            except Exception as e:  # pragma: no cover
                logger.warning(e)
                raise Exception("Error: Cannot Write to File: %s" % _file)

    def generate_rhsm_facts(self):
        logger.info('Writing RHSM facts to %s ...', self.rhsm_facts_file)

        hostname = self.obfuscate.get('hostname')
        hn_mapping = hostname.mapping() if hostname else []

        keyword = self.obfuscate.get('keyword')
        kw_mapping = keyword.mapping() if keyword else []

        ipv4 = self.obfuscate.get('ipv4')
        ipv4_mapping = ipv4.mapping() if ipv4 else []

        ipv6 = self.obfuscate.get('ipv6')
        ipv6_mapping = ipv6.mapping() if ipv6 else []

        mac = self.obfuscate.get('mac')
        mac_mapping = mac.mapping() if mac else []

        facts = {
            'insights_client.hostname': self.fqdn,
            'insights_client.obfuscate_ipv4_enabled': 'ipv4' in self.obfuscate,
            'insights_client.obfuscate_ipv6_enabled': 'ipv6' in self.obfuscate,
            'insights_client.obfuscate_hostname_enabled': 'hostname' in self.obfuscate,
            'insights_client.obfuscate_mac_enabled': 'mac' in self.obfuscate,
            'insights_client.obfuscated_ipv4': json.dumps(ipv4_mapping),
            'insights_client.obfuscated_ipv6': json.dumps(ipv6_mapping),
            'insights_client.obfuscated_mac': json.dumps(mac_mapping),
            'insights_client.obfuscated_hostname': json.dumps(hn_mapping),
            'insights_client.obfuscated_keyword': json.dumps(kw_mapping),
        }

        write_report(facts, self.rhsm_facts_file)

    def generate_report(self, archive_name):
        # Always generate the rhsm.facts files
        self.generate_rhsm_facts()
        # Generate CSV reports accordingly
        for parser in list(self.redact.values()) + list(self.obfuscate.values()):
            if parser:
                parser.generate_report(self.report_dir, archive_name)
