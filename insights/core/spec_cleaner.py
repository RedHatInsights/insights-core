"""
Clean the collected specs (files/commands/datasources)
======================================================

The following processes will be applied to clean the collected specs:

    - Redaction
      This is a must-be-done operation to all the collected specs.

    - Obfuscation
      Obfuscate the IP or Hostname appears in the spec content according to the
      specs native requirement and user configuration.

"""
import logging
import hashlib
import json
import os
import re
import six
import socket
import struct

# TODO: getting RHSM facts file from the InsightsConstants directly
# from insights.client.constants import InsightsConstants as constants
from insights.util.hostname import determine_hostname
from insights.util.posix_regex import replace_posix

logger = logging.getLogger(__name__)

DEFAULT_PASSWORD_REGEXS = [
    r"(password[a-zA-Z0-9_]*)(\s*\:\s*\"*\s*|\s*\"*\s*=\s*\"\s*|\s*=+\s*|\s*--md5+\s*|\s*)([a-zA-Z0-9_!@#$%^&*()+=/-]+)",
    r"(password[a-zA-Z0-9_]*)(\s*\*+\s+)(.+)",
]
"""The regex for password removal, which is read from the "/etc/insights-client/.exp.sed"."""


def write_report(report, report_file, mode=0o644):
    # Get the current umask
    umask = os.umask(0o022)
    # Reset the umask
    os.umask(umask)
    try:
        with open(report_file, 'w') as fp:
            if isinstance(report, dict):
                json.dump(report, fp)
            elif isinstance(report, list):
                for line in report:
                    fp.write("{0}\n".format(line))
        # Change the file mode per the current umask
        os.chmod(report_file, mode & ~umask)
    except (IOError, OSError) as e:
        logger.error('Could not write to %s: %s', report_file, str(e))


class Cleaner(object):
    def __init__(self, config, rm_conf, fqdn=None):
        self.report_dir = '/tmp'
        # Obfuscation - set: ip and hostname only
        self.obfuscate = set()
        self.obfuscate.add('ip') if config and config.obfuscate else None
        self.obfuscate.add('hostname') if config and config.obfuscate_hostname else None

        # File Content Redaction
        # - Pattern redaction
        rm_conf = rm_conf or {}
        exclude = rm_conf.get('patterns', [])
        regex = False
        if isinstance(exclude, dict) and exclude.get('regex'):
            exclude = [r'%s' % replace_posix(i) for i in exclude['regex']]
            regex = True
        self.redact = dict(exclude=exclude, regex=regex)

        # - Keyword replacement redact information
        #   Keyword replacement does NOT depend on "obfuscate=True"
        keywords = rm_conf.get('keywords')
        self.kw_db = dict()  # keyword database
        self.kws = set()     # keywords that have been replaced
        self._keywords2db(keywords)

        # Obfuscation
        fqdn = fqdn if fqdn else determine_hostname()
        name_list = fqdn.split('.')
        self.hostname = name_list[0]
        self.fqdn = fqdn
        self.domain = None if len(name_list) <= 1 else '.'.join(name_list[1:])

        # - IP obfuscate information
        self.ip_db = dict()  # IP database
        self.start_ip = '10.230.230.1'

        # - Hostname obfuscate information
        self.hn_db = dict()  # hostname database
        self.hostname_count = 0
        self.obfuscated_fqdn = None
        self.obfuscated_domain = 'example.com'  # right now this needs to be a 2nd level domain, like foo.com, example.com, domain.org, etc.

        # - Domain name obfuscate information
        self.dn_db = dict()  # domain name database
        self.domain_count = 0

        if config and config.obfuscate_hostname and self.fqdn:
            self._domains2db()
            hashed_hostname = hashlib.sha1(
                    self.fqdn.encode('utf-8')
                    if six.PY3 else self.fqdn).hexdigest()[:12]
            self.obfuscated_fqdn = '{0}.example.com'.format(hashed_hostname)
            self.hostname_count += 1
            self.hn_db[self.obfuscated_fqdn] = self.fqdn
            # per https://access.redhat.com/documentation/en-us/red_hat_insights/2023/html/client_configuration_guide_for_red_hat_insights/con-insights-client-cg-data-obfuscation_insights-cg-obfuscation#proc-obfuscating-hostname_insights-cg-obfuscation
            # only `hostname` is obfuscated

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
                logger.debug("Obfuscated Domain Created - %s -> %s" % (self.domain, self.obfuscated_domain))

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
        if not line:
            return line
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

        except Exception as e:  # pragma: no cover
            logger.warning(e)

    def _sub_keywords(self, line):
        # this will substitute out any keyword entries on a given line
        if not line:
            return line
        for k, v in self.kw_db.items():
            if k in line:
                line = line.replace(k, v)
                self.kws.add(k)
                logger.debug("Replacing Keyword - %s > %s", k, v)
        return line

    ###########################
    #   Main functions        #
    ###########################

    def _obfuscate_line(self, line, obf_funcs):
        # obfuscate line for possible hostname, ip
        if not line:
            return line
        for func in obf_funcs:
            tmp_line = func(line)
            line = tmp_line
        return line

    def _redact_line(self, line):
        # redact line per the file-content-redaction.yaml
        if not line:
            return line
        # 1. patterns removal
        find = re.search if self.redact['regex'] else lambda x, y: x in y
        if any(find(pat, line) for pat in self.redact.get('exclude', [])):
            logger.debug("Pattern matched, removing line: %s" % line.strip())
            # patterns found, remove it
            return None
        # 2. password removal
        for regex in DEFAULT_PASSWORD_REGEXS:
            tmp_line = line
            line = re.sub(regex, r"\1\2********", tmp_line)
            if line != tmp_line:
                break
        # 3. keyword replacement redaction
        return self._sub_keywords(line)

    def get_obfuscate_functions(self, filename='', no_obfuscate=None):
        """
        Return the list of required obfuscation function according to the
        filename and configuration.  By default, it returns:
            - [] when obfuscate=False
            - [self._sub_ip] when obfuscate=True Only
            - [self._sub_hostname, self._sub_ip] when obfuscate_hostname=True
        """
        obf_funcs = []
        # Get the actual obfuscate list setting for this file
        obfs = set(self.obfuscate) - set(no_obfuscate or [])
        # IP obfuscation entry
        obf_funcs.append(self._sub_ip_netstat if filename.endswith("netstat_-neopa") else self._sub_ip) if "ip" in obfs else None
        # Hostname obfuscation entry
        obf_funcs.append(self._sub_hostname) if "hostname" in obfs else None
        return obf_funcs

    def clean_content(self, lines, obf_funcs=None, no_redact=False):
        """
        Clean lines one by one according to the configuration, the cleaned
        lines will be returned.
        """
        def _clean_line(_line):
            # 1. Do Redaction by default, unless "no_redact=True"
            if _line and not no_redact:
                _line = self._redact_line(_line)
            # 2. Do Obfuscation as per the "obf_funcs"
            _line = self._obfuscate_line(_line, obf_funcs or [])
            return _line

        # handle single string
        if not isinstance(lines, list):
            return _clean_line(lines)

        result = []
        for line in lines:
            line = _clean_line(line)
            result.append(line) if line is not None else None
        if result and list(filter(None, result)):
            # When there are some lines Truth
            return result
        # All lines blank
        return []

    def clean_file(self, _file, no_obfuscate=None, no_redact=False):
        """
        Clean a file according to the configuration, the file will be updated
        directly with the cleaned content.
        """
        logger.debug('Cleaning %s ...' % _file)

        if os.path.exists(_file) and not os.path.islink(_file):
            # Process the file
            raw_data = content = None
            obf_funcs = self.get_obfuscate_functions(_file, no_obfuscate)
            try:
                with open(_file, 'r') as fh:
                    raw_data = fh.readlines()
                    content = self.clean_content(raw_data, obf_funcs, no_redact)
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

    def generate_rhsm_facts(self, rhsm_facts_file):
        logger.info('Writing RHSM facts to %s ...', rhsm_facts_file)

        hn_block = []
        for k, v in self.hn_db.items():
            hn_block.append({'original': v, 'obfuscated': k})

        kw_block = []
        for k in self.kws:
            kw_block.append({'original': k, 'obfuscated': self.kw_db[k]})

        ip_block = []
        for k, v in self.ip_db.items():
            ip_block.append(
                {
                    'original': self._int2ip(v),
                    'obfuscated': self._int2ip(k)
                })

        facts = {
            'insights_client.hostname': self.fqdn,
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
            for k in self.kws:
                lines.append('{0},{1}'.format(k, self.kw_db[k]))
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise Exception('CreateReport Error: Error Creating Keyword Report')

        write_report(lines, kw_report_file)

        logger.info('Completed Keyword Report.')

    def generate_report(self, archive_name, rhsm_facts_file):
        # Always generate the rhsm.facts files
        self.generate_rhsm_facts(rhsm_facts_file)
        if 'ip' in self.obfuscate:
            self.generate_ip_report(archive_name)
        if 'hostname' in self.obfuscate:
            self.generate_hn_report(archive_name)
        if self.kws:
            self.generate_kw_report(archive_name)
