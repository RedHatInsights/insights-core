"""
Clean the collected specs (files/commands/datasources)
======================================================

The following processes will be applied to clean the collected specs:

    - Redaction
      This is a must-be-done operation to all the collected specs.

    - Obfuscation
      Obfuscate the IP or Hostname appears in the spec content according to the
      specs native requirement and user configuration.

    - Filter (T.B.D)
      If a spec is specified as `filterable=True`, the insights core collection
      will only collect the lines that only contains the keywords listed in the
      filters list and save into the archive.

"""
import logging
import hashlib
import json
import os
import re
import six
import socket
import struct

from tempfile import TemporaryFile

from insights.client.constants import InsightsConstants as constants
from insights.util.hostname import determine_hostname
from insights.util.posix_regex import replace_posix

logger = logging.getLogger(__name__)

DEFAULT_PASSWORD_REGEXS = [
    "(password[a-zA-Z0-9_]*)(\s*\:\s*\"*\s*|\s*\"*\s*=\s*\"\s*|\s*=+\s*|\s*--md5+\s*|\s*)([a-zA-Z0-9_!@#$%^&*()+=/-]*)",
    "(password[a-zA-Z0-9_]*)(\s*\*+\s+)(.+)",
]
"""The regex for password removal, which is read from the "/etc/insights-client/.exp.sed"."""
EXCLUDE_FILES = (
    'etc/insights-client/machine-id',
    'etc/machine-id',
)
"""The files to ignore."""


def write_report(report, report_file):
    try:
        with open(report_file, 'w') as fp:
            if isinstance(report, dict):
                json.dump(report, fp)
            elif isinstance(report, list):
                for line in report:
                    fp.write("{0}\n".format(line))
    except (IOError, OSError) as e:
        logger.error('Could not write to %s: %s', report_file, str(e))


class Cleaner(object):
    def __init__(self, config, rm_conf, fqdn=None):

        # core parses blacklist for files and commands as regex
        def _regextive(keywords):
            if config.core_collect:
                for idx, f in enumerate(keywords):
                    keywords[idx] = '^' + f + '$'
            return keywords

        self.report_dir = '/tmp'
        # Obfuscation - set: ip and hostname only
        self.obfuscate = set()
        self.obfuscate.add('ip') if config.obfuscate else None
        self.obfuscate.add('hostname') if config.obfuscate_hostname else None

        # Redaction - dict:
        rm_conf = rm_conf or {}
        exclude = rm_conf.get('patterns', [])
        regex = False
        if isinstance(exclude, dict) and exclude.get('regex'):
            exclude = [r'%s' % replace_posix(i) for i in exclude['regex']]
            regex = True
        self.redact = dict(
            exclude=exclude,
            regex=regex,
            files=_regextive(rm_conf.get('files', [])),
            commands=_regextive(rm_conf.get('commands', [])),
            components=rm_conf.get('components', []))

        # Hostname of the current host
        fqdn = fqdn if fqdn else determine_hostname(config.display_name)
        name_list = fqdn.split('.')
        self.hostname = name_list[0]
        self.fqdn = fqdn
        self.domain = None if len(name_list) <= 1 else '.'.join(name_list[1:])

        # IP obfuscate information
        self.ip_db = dict()  # IP database
        self.start_ip = '10.230.230.1'

        # Hostname obfuscate information
        self.hn_db = dict()  # hostname database
        self.hostname_count = 0
        self.obfuscated_fqdn = None
        self.obfuscated_domain = 'example.com'  # right now this needs to be a 2nd level domain, like foo.com, example.com, domain.org, etc.

        # Domain name obfuscate information
        self.dn_db = dict()  # domain name database
        self.domain_count = 0

        # Keyword obfuscate information
        keywords = rm_conf.get('keywords')
        self.kw_db = dict()  # keyword database
        self.kw_count = 0
        if self.obfuscate:
            self._keywords2db(keywords)

        if config.obfuscate_hostname and self.fqdn:
            self._domains2db()
            hashed_hostname = hashlib.sha1(
                    self.fqdn.encode('utf-8')
                    if six.PY3 else self.fqdn).hexdigest()[:12]
            self.obfuscated_fqdn = '{0}.example.com'.format(hashed_hostname)
            self.hn_db[self.obfuscated_fqdn] = self.fqdn  # we'll prime the hostname pump to clear out a ton of useless logic later
            # As per https://access.redhat.com/documentation/en-us/red_hat_insights/2023/html/client_configuration_guide_for_red_hat_insights/con-insights-client-cg-data-obfuscation_insights-cg-obfuscation#proc-obfuscating-hostname_insights-cg-obfuscation
            # only `hostname` is obfuscated
            # self._process_hosts_file()  # we'll take a dig through the hosts file and make sure it is as scrubbed as possible

    ###########################
    #   IP functions          #
    ###########################

    def _ip2int(self, ipstr):
        # converts a dotted decimal IP address into an integer that can be incremented
        return struct.unpack('!I', socket.inet_aton(ipstr))[0]

    def _int2ip(self, num):
        # converts an integer stored in the IP database into a dotted decimal IP
        return socket.inet_ntoa(struct.pack('!I', num))

    def _ip2db(self, ip):
        '''
        adds an IP address to the IP database and returns the obfuscated entry, or returns the
        existing obfuscated IP entry
        FORMAT:
        {$obfuscated_ip: $original_ip,}
        '''
        ip_num = self._ip2int(ip)
        ip_found = False
        db = self.ip_db
        for k, v in db.items():
            if v == ip_num:
                ret_ip = self._int2ip(k)
                ip_found = True
        if ip_found:                # the entry already existed
            return ret_ip
        else:                       # the entry did not already exist
            if len(self.ip_db) > 0:
                new_ip = max(db.keys()) + 1
            else:
                new_ip = self._ip2int(self.start_ip)
            db[new_ip] = ip_num

            return self._int2ip(new_ip)

    def _sub_ip(self, line):
        '''
        This will substitute an obfuscated IP for each instance of a given IP in a file
        This is called in the self._clean_line function, along with user _sub_* functions to scrub a given
        line in a file.
        It scans a given line and if an IP exists, it obfuscates the IP using _ip2db and returns the altered line
        '''
        try:
            pattern = r"(((\b25[0-5]|\b2[0-4][0-9]|\b1[0-9][0-9]|\b[1-9][0-9]|\b[1-9]))(\.(\b25[0-5]|\b2[0-4][0-9]|\b1[0-9][0-9]|\b[1-9][0-9]|\b[0-9])){3})"
            ips = [each[0] for each in re.findall(pattern, line)]
            if len(ips) > 0:
                for ip in sorted(ips, key=len, reverse=True):
                    # skip loopback (https://github.com/RedHatInsights/insights-core/issues/3230#issuecomment-924859845)
                    if ip != "127.0.0.1" and ip in line:
                        new_ip = self._ip2db(ip)
                        logger.debug("Obfuscating IP - %s > %s", ip, new_ip)
                        line = line.replace(ip, new_ip)
            return line
        except Exception as e:  # pragma: no cover
            logger.warning(e)
            raise Exception('SubIPError: Unable to Substitute IP Address - %s', ips)

    def _sub_ip_netstat(self, line):
        '''
        Special version of _sub_ip for netstat to preserve spacing
        '''
        try:
            pattern = r"(((\b25[0-5]|\b2[0-4][0-9]|\b1[0-9][0-9]|\b[1-9][0-9]|\b[1-9]))(\.(\b25[0-5]|\b2[0-4][0-9]|\b1[0-9][0-9]|\b[1-9][0-9]|\b[0-9])){3})"
            ips = [each[0] for each in re.findall(pattern, line)]
            if len(ips) > 0:
                for ip in sorted(ips, key=len, reverse=True):
                    # skip loopback (https://github.com/RedHatInsights/insights-core/issues/3230#issuecomment-924859845)
                    if ip != "127.0.0.1" and ip in line:
                        ip_len = len(ip)
                        new_ip = self._ip2db(ip)
                        new_ip_len = len(new_ip)
                        logger.debug("Obfuscating IP - %s > %s", ip, new_ip)
                        # pad or remove spaces to allow for the new length
                        if ip_len > new_ip_len:
                            numspaces = ip_len - new_ip_len
                            line = line.replace(ip, new_ip)

                            # shift past port specification to add spaces
                            idx = line.index(new_ip) + new_ip_len
                            c = line[idx]
                            while c != " ":
                                idx += 1
                                if idx == len(line):
                                    idx = len(line) - 1
                                    break
                                c = line[idx]
                            line = line[0:idx] + numspaces * " " + line[idx:]

                        elif new_ip_len > ip_len:
                            numspaces = new_ip_len - ip_len
                            line = line.replace(ip, new_ip)

                            # shift past port specification to skip spaces
                            idx = line.index(new_ip) + new_ip_len
                            c = line[idx]
                            while c != " ":
                                idx += 1
                                if idx == len(line):
                                    break
                                c = line[idx]
                            line = line[0:idx] + line[(idx + numspaces):]

                        else:
                            line = line.replace(ip, new_ip)
            return line
        except Exception as e:  # pragma: no cover
            logger.warning(e)
            raise Exception('SubIPError: Unable to Substitute IP Address - %s', ip)

    #############################
    # Hostname Domain Functions #
    #############################

    def _domains2db(self):
        # adds any additional domainnames to the domain database to be searched for
        try:
            # we will add the root domain for an FQDN as well.
            if self.domain is not None:
                self.dn_db[self.obfuscated_domain] = self.domain
                logger.warning("Obfuscated Domain Created - %s -> %s" % (self.domain, self.obfuscated_domain))

            self.domain_count = len(self.dn_db)
            return True
        except Exception as e:  # pragma: no cover
            logger.warning(e)

    def _hn2db(self, hn):
        '''
        This will add a hostname for a hostname for an included domain or return an existing entry
        '''
        db = self.hn_db
        hn_found = False
        for k, v in db.items():
            if v == hn:  # the hostname is in the database
                ret_hn = k
                hn_found = True
        if hn_found:
            return ret_hn
        else:
            self.hostname_count += 1  # we have a new hostname, so we increment the counter to get the host ID number
            o_domain = self.obfuscated_domain
            for od, d in self.dn_db.items():
                if d in hn:  # never false
                    o_domain = od
            new_hn = "host%s.%s" % (self.hostname_count, o_domain)
            self.hn_db[new_hn] = hn
            return new_hn

    def _sub_hostname(self, line):
        '''
        This will replace the exact hostname and all instances of the domain name with the obfuscated alternatives.
        Example:
        '''
        try:
            for od, d in self.dn_db.items():
                # regex = re.compile(r'\w*\.%s' % d)
                regex = re.compile(r'(?![\W\-\:\ \.])[a-zA-Z0-9\-\_\.]*\.%s' % d)
                hostnames = [each for each in regex.findall(line)]
                if len(hostnames) > 0:
                    for hn in hostnames:
                        new_hn = self._hn2db(hn)
                        logger.debug("Obfuscating FQDN - %s > %s", hn, new_hn)
                        line = line.replace(hn, new_hn)
            if self.hostname:
                line = line.replace(self.hostname, self._hn2db(self.fqdn))  # catch any non-fqdn instances of the system hostname
            return line
        except Exception as e:  # pragma: no cover
            logger.warning(e)
            raise Exception('SubHostnameError: Unable to Substitute Hostname/Domainname')

    ###########################
    #   Keyword functions     #
    ###########################

    def _keywords2db(self, keywords):
        # processes optional keywords to add to be obfuscated
        try:
            if keywords:
                k_count = 0
                for keyword in keywords:
                    o_kw = "keyword%s" % k_count
                    self.kw_db[keyword.rstrip()] = o_kw
                    logger.debug("Added Obfuscated Keyword - %s", o_kw)
                    k_count += 1
                logger.debug("Added Keyword Contents from Customer's configuration")
                self.kw_count = k_count

        except Exception as e:  # pragma: no cover
            logger.warning(e)

    def _kw2db(self, keyword):
        return self.kw_db[keyword]

    def _sub_keywords(self, line):
        # this will substitute out any keyword entries on a given line
        if self.kw_count > 0:    # we have obfuscated keywords to work with
            for k in self.kw_db.keys():
                if k in line:
                    line = line.replace(k, self._kw2db(k))
                    logger.debug("Obfuscating Keyword - %s > %s", k, self._kw2db(k))
        return line

    ###########################
    #   Main functions        #
    ###########################

    def _obfuscate_line(self, line, obfs, ip_func):
        '''this will return a line with obfuscates for all possible variables, hostname, ip, etc.'''
        new_line = line
        if "ip" in obfs:
            new_line = ip_func(line)                 # IP substitution
        if "hostname" in obfs:
            new_line = self._sub_hostname(new_line)  # Hostname substitution
        if self.obfuscate and hasattr(self, 'kw_db'):
            # keywords obfuscate depends on "obfuscate=True"
            new_line = self._sub_keywords(new_line)  # Keyword Substitution
        return new_line

    def _redact_line(self, line):
        # patterns removal
        new_line = line
        find = re.search if self.redact['regex'] else lambda x, y: x in y
        if any(find(pat, new_line) for pat in self.redact.get('exclude', [])):
            # patterns found, remove it
            return None
        # password removal
        for regex in DEFAULT_PASSWORD_REGEXS:
            tmp_line = new_line
            new_line = re.sub(regex, r"\1\2********", tmp_line)
            if new_line != tmp_line:
                break
        return new_line

    def clean_file(self, _file, filters=None, obfs=None):
        def _determine_ip_func(filepath):
            ip_func = self._sub_ip
            if _file.endswith("netstat_-neopa"):
                ip_func = self._sub_ip_netstat
            return ip_func

        if _file.endswith(EXCLUDE_FILES):
            # do not redact or obfuscate the selected files
            return

        # filters = filters or []
        obfs = obfs or []
        logger.debug('Cleaning %s %s ...', list(obfs) if obfs else '[Redacting]', _file)

        if os.path.exists(_file) and not os.path.islink(_file):
            ip_func = _determine_ip_func(_file)
            data = None
            tmp_file = TemporaryFile(mode='w+b')
            # Process it
            try:
                with open(_file, 'r') as fh:
                    data = fh.readlines()
                    if data:
                        for line in data:
                            # Do Redaction without condition
                            new_l = self._redact_line(line)
                            if new_l is None:
                                # line is removed after redaction
                                continue
                            # Do Obfuscation as per the "obfs"
                            new_l = self._obfuscate_line(new_l, obfs, ip_func)
                            # Do `filter` as per the "filters"
                            # new_l = self._grep_line(line, filters)
                            tmp_file.write(new_l.encode('utf-8') if six.PY3 else new_l)
                        tmp_file.seek(0)
            except Exception as e:  # pragma: no cover
                logger.warning(e)
                raise Exception("Error: Cannot Open File for Obfuscating/Redacting - %s" % _file)
            # Store it
            try:
                if data:
                    with open(_file, 'wb') as new_fh:
                        for line in tmp_file:
                            new_fh.write(line)
            except Exception as e:  # pragma: no cover
                logger.warning(e)
                raise Exception("Error: Cannot Write to New File - %s" % _file)

            finally:
                tmp_file.close()

    def generate_rhsm_facts(self, rhsm_facts_file):
        logger.info('Writing RHSM facts to %s ...', rhsm_facts_file)

        hn_block = []
        for k, v in self.hn_db.items():
            hn_block.append({'original': k, 'obfuscated': v})

        kw_block = []
        for k, v in self.kw_db.items():
            kw_block.append({'original': k, 'obfuscated': v})

        ip_block = []
        for k, v in self.ip_db.items():
            ip_block.append(
                {
                    'original': self._int2ip(v),
                    'obfuscated': self._int2ip(k)
                })

        facts = {
            'insights_client.hostname': self.obfuscated_fqdn,
            'insights_client.obfuscate_ip_enabled': 'ip' in self.obfuscate,
            'insights_client.ips': json.dumps(ip_block),
            'insights_client.obfuscate_hostname_enabled': 'hostname' in self.obfuscate,
            'insights_client.hostnames': json.dumps(hn_block),
            'insights_client.keywords': json.dumps(kw_block),
        }

        write_report(facts, rhsm_facts_file)

    def generate_ip_report(self, archive_name):
        try:
            ip_report_file = os.path.join(self.report_dir, "%s-ip.csv" % archive_name)
            logger.info('Creating IP Report - %s', ip_report_file)
            lines = ['Obfuscated IP,Original IP']
            for k, v in self.ip_db.items():
                lines.append('{0},{1}'.format(self._int2ip(k), self._int2ip(v)))
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise Exception('CreateReport Error: Error Creating IP Report')

        write_report(lines, ip_report_file)

        logger.info('Completed IP Report.')

    def generate_hn_report(self, archive_name):
        try:
            hn_report_file = os.path.join(self.report_dir, "%s-hostname.csv" % archive_name)
            logger.info('Creating Hostname Report - %s', hn_report_file)
            lines = ['Obfuscated Hostname,Original Hostname']
            if self.hostname_count > 0:
                for k, v in self.hn_db.items():
                    lines.append('{0},{1}'.format(k, v))
            else:
                lines.append('None,None')
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise Exception('CreateReport Error: Error Creating Hostname Report')

        write_report(lines, hn_report_file)

        logger.info('Completed Hostname Report.')

    def generate_kw_report(self, archive_name):
        try:
            kw_report_file = os.path.join(self.report_dir, "%s-keyword.csv" % archive_name)
            logger.info('Creating Keyword Report - %s', kw_report_file)
            lines = ['Replaced Keyword,Original Keyword']
            for k, v in self.kw_db.items():
                lines.append('{0},{1}'.format(k, v))
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise Exception('CreateReport Error: Error Creating Keyword Report')

        write_report(lines, kw_report_file)

        logger.info('Completed Keyword Report.')

    def generate_report(self, archive_name):
        if self.obfuscate or self.kw_count > 0:
            self.generate_rhsm_facts(constants.rhsm_facts_file)
            if 'ip' in self.obfuscate:
                self.generate_ip_report(archive_name)
            if 'hostname' in self.obfuscate:
                self.generate_hn_report(archive_name)
            if self.kw_count:
                self.generate_kw_report(archive_name)
