"""
Clean collected specs (files/commands)
======================================

The following processes will be applied to the collected specs:

- Redaction (patterns redaction)
  This is a must-be-done operation to all the collected specs.

- Filtering
  Filter line as per the allow list got from the "filters.yaml"

- Obfuscation (IPv4, [IPv6], Hostname, MAC, Password, Keywords)
  Obfuscate lines in spec content according to the user configuration and
  specs requirement.
"""

import logging
import json
import os
import six

from insights.cleaner.filters import AllowFilter
from insights.cleaner.hostname import Hostname
from insights.cleaner.ip import IPv4  # IPv6
from insights.cleaner.keyword import Keyword

# from insights.cleaner.mac import Mac
from insights.cleaner.password import Password
from insights.cleaner.pattern import Pattern
from insights.cleaner.utilities import write_report
from insights.util.hostname import determine_hostname
from insights.util.posix_regex import replace_posix

logger = logging.getLogger(__name__)
DEFAULT_OBFUSCATIONS = {
    'hostname',
    'ip',  # ipv4
    'ipv6',
    'keyword',
    'mac',
    'password',
}  # set


class Cleaner(object):
    def __init__(self, config, rm_conf, fqdn=None):
        self.report_dir = '/tmp'  # FIXME
        self.rhsm_facts_file = getattr(
            config, 'rhsm_facts_file', os.path.join(self.report_dir, 'insights-client.facts')
        )
        # User Configuration
        rm_conf = rm_conf or {}
        exclude = rm_conf.get('patterns', [])
        regex = False
        if isinstance(exclude, dict) and exclude.get('regex'):
            exclude = [r'%s' % replace_posix(i) for i in exclude['regex']]
            regex = True
        # - Pattern redaction and allow-list filter
        self.redact = {
            'pattern': Pattern(exclude, regex) if exclude else None,
            'allow_filter': AllowFilter(),
        }
        # - Keyword and Password replacement
        keywords = rm_conf.get('keywords')
        self.obfuscate = {
            'keyword': Keyword(keywords) if keywords else None,
            'password': Password(),
        }

        self.fqdn = fqdn if fqdn else determine_hostname()
        if config and config.obfuscate:
            # - IPv4 obfuscation
            self.obfuscate.update(ip=IPv4())
            # # - IPv6 obfuscation
            # self.obfuscate.update(ipv6=IPv6()) if config.obfuscate_ipv6 else None
            # - Hostname obfuscation
            (
                self.obfuscate.update(hostname=Hostname(self.fqdn))
                if config.obfuscate_hostname
                else None
            )
            # # - MAC obfuscation
            # self.obfuscate.update(mac=Mac()) if config.obfuscate_mac else None

    def clean_content(self, lines, no_obfuscate=None, no_redact=False, allowlist=None, width=False):
        """
        Clean lines one by one according to the configuration, the cleaned
        lines will be returned.
        """

        def _clean_line(line):
            for parser, kwargs in parsers:
                line = parser.parse_line(line, **kwargs)
            return line

        parsers = list()  # List of parsers to be applied with order
        # 1. Redact when NO "no_redact=True" is set
        if self.redact['pattern'] and not no_redact:
            parsers.append((self.redact['pattern'], {})) if not no_redact else None
        # 2. Filter as per allowlist got from add_filter
        (
            parsers.append((self.redact['allow_filter'], {'allowlist': allowlist}))
            if allowlist is not None
            else None
        )
        # 3. Obfuscation entries
        # - Keyword
        # - Password
        # - IPv4
        # - IPv6
        # - Hostname
        # - Mac
        no_obfuscate.append('ipv6') if no_obfuscate and 'ip' in no_obfuscate else None
        for obf in set(self.obfuscate.keys()) - set(no_obfuscate or []):
            if self.obfuscate[obf]:
                parsers.append((self.obfuscate[obf], {'width': width}))

        # handle single string
        if not isinstance(lines, list):
            return _clean_line(lines)

        result = []
        for line in lines:
            line = _clean_line(line)
            result.append(line) if line is not None else None
        if result and any(l for l in result):
            # When there are some lines Truth
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

        hn_block = []
        hostname = self.obfuscate.get('hostname')
        if hostname:
            for k, v in hostname.hn_db.items():
                hn_block.append({'original': v, 'obfuscated': k})

        kw_block = []
        keyword = self.obfuscate.get('keyword')
        if keyword:
            for k in keyword.obfuscated:
                kw_block.append({'original': k, 'obfuscated': keyword.kw_db[k]})

        ip_block = []
        ipv4 = self.obfuscate.get('ip')
        if ipv4:
            for k, v in ipv4.ip_db.items():
                ip_block.append({'original': ipv4._int2ip(v), 'obfuscated': ipv4._int2ip(k)})

        facts = {
            'insights_client.hostname': self.fqdn,
            'insights_client.obfuscate_ip_enabled': 'ip' in self.obfuscate,
            'insights_client.ips': json.dumps(ip_block),
            'insights_client.obfuscate_hostname_enabled': 'hostname' in self.obfuscate,
            'insights_client.hostnames': json.dumps(hn_block),
            'insights_client.keywords': json.dumps(kw_block),
        }

        write_report(facts, self.rhsm_facts_file)

    def generate_report(self, archive_name):
        # Always generate the rhsm.facts files
        self.generate_rhsm_facts()
        # Generate CSV reports accordingly
        for parser in list(self.redact.values()) + list(self.obfuscate.values()):
            if parser:
                parser.generate_report(self.report_dir, archive_name)
