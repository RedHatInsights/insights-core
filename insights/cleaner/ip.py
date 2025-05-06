"""
IP Obfuscation
==============
The following cleaners are included in this module:

IPv4 Obfuscation
----------------

IPv6 Obfuscation
----------------

"""

import hashlib
import logging
import os
import re
import six
import socket
import struct

from insights.cleaner.utilities import write_report

logger = logging.getLogger(__name__)


class IPv4(object):
    """
    Class for obfuscating IPv4.
    """

    def __init__(self):
        # - IP obfuscate information
        self._ip_db = dict()  # IP database
        self._start_ip = '10.230.230.1'
        self._ignore_list = ["127.0.0.1"]
        # self.pattern = r'((?<!(\.|\d))([0-9]{1,3}\.){3}([0-9]){1,3}(\/([0-9]{1,2}))?)'
        self.pattern = r"(((\b25[0-5]|\b2[0-4][0-9]|\b1[0-9][0-9]|\b[1-9][0-9]|\b[1-9]))(\.(\b25[0-5]|\b2[0-4][0-9]|\b1[0-9][0-9]|\b[1-9][0-9]|\b[0-9])){3})"

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
        db = self._ip_db
        for k, v in db.items():
            if v == ip_num:
                ret_ip = self._int2ip(k)
                ip_found = True
        if ip_found:  # the entry already existed
            return ret_ip
        else:  # the entry did not already exist
            if len(self._ip_db) > 0:
                new_ip = max(db.keys()) + 1
            else:
                new_ip = self._ip2int(self._start_ip)
            db[new_ip] = ip_num

            return self._int2ip(new_ip)

    def parse_line(self, line, **kwargs):
        '''
        This will substitute an obfuscated IP for each instance of a given IP in a file
        It scans a given line and if an IP exists, it obfuscates the IP using _ip2db and returns the altered line
        '''

        def _sub_ip(line, ip):
            new_ip = self._ip2db(ip)
            logger.debug("Obfuscating IPv4 - %s > %s", ip, new_ip)
            return line.replace(ip, new_ip)

        def _sub_ip_keep_width(line, ip):
            ip_len = len(ip)
            new_ip = self._ip2db(ip)
            new_ip_len = len(new_ip)
            logger.debug("Obfuscating IPv4 - %s > %s", ip, new_ip)
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
                return line[0:idx] + numspaces * " " + line[idx:]
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
                return line[0:idx] + line[(idx + numspaces) :]
            else:
                return line.replace(ip, new_ip)

        if not line:
            return line
        try:
            ips = [each[0] for each in re.findall(self.pattern, line)]
            for ip in sorted(ips or [], key=len, reverse=True):
                if ip not in self._ignore_list:  # ip must in line
                    if kwargs.get('width', False):
                        line = _sub_ip_keep_width(line, ip)
                    else:
                        line = _sub_ip(line, ip)
            return line
        except Exception as e:  # pragma: no cover
            logger.warning(e)
            raise Exception('SubIPError: Unable to Substitute IPv4 Address - %s', ips)

    def mapping(self):
        mapping = []
        for k, v in self._ip_db.items():
            mapping.append({'original': self._int2ip(v), 'obfuscated': self._int2ip(k)})
        return mapping

    def generate_report(self, report_dir, archive_name):
        try:
            ip_report_file = os.path.join(report_dir, "%s-ipv4.csv" % archive_name)
            logger.info('Creating IPv4 Report - %s', ip_report_file)
            lines = ['Obfuscated IPv4,Original IPv4']
            for k, v in self._ip_db.items():
                lines.append('{0},{1}'.format(self._int2ip(k), self._int2ip(v)))
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise Exception('CreateReport Error: Error Creating IPv4 Report')

        write_report(lines, ip_report_file)

        logger.info('Completed IPv4 Report.')


class IPv6(object):
    """
    Class for obfuscating IPv6.
    """

    def __init__(self):
        self._ipv6_db = dict()  # IPv6 database
        # Ignore list for IPv6
        self._ignore_list = [r'\s+']  # ignore whitespace
        # IPv6 pattern, stolen from sos
        # FIXME:
        #   This pattern is not perfect, e.g. it cannot match "::1" perfectly.
        #   Hence, we add the above ignore list to avoid the roughly match that
        #   includes whitespace.
        self.pattern = (
            r"(?<![:\\.\\-a-z0-9])((([0-9a-f]{1,4})(:[0-9a-f]{1,4}){7})|"
            r"(([0-9a-f]{1,4}(:[0-9a-f]{0,4}){0,5}))([^.])::(([0-9a-f]{1,4}"
            r"(:[0-9a-f]{1,4}){0,5})?))(/\d{1,3})?(?![:\\a-z0-9])"
        )

    def _ip2db(self, ip):
        '''
        Add an IPv6 address to IPv6 database and return obfuscated address.

        FORMAT:
        {$original_ip:, $obfuscated_ip}
        '''

        def obfuscate_hex(_hex):
            if _hex:
                n_0_hex = _hex.lstrip('0').lower()
                if n_0_hex:
                    old_hex = n_0_hex.encode('utf-8') if six.PY3 else n_0_hex
                    new_hex = hashlib.sha1(old_hex).hexdigest()[: len(old_hex)]
                    return '0' * (len(_hex) - len(n_0_hex)) + new_hex
                return '0' * len(_hex)
            return ''

        try:
            if ip in self._ipv6_db:
                return self._ipv6_db[ip]
            if ip in self._ipv6_db.values():  # pragma: no cover
                # avoid nested obfuscating
                return None
            self._ipv6_db[ip] = ':'.join(obfuscate_hex(h) for h in ip.split(':'))
            return self._ipv6_db[ip]
        except Exception as e:  # pragma: no cover
            logger.warning(e)
            raise Exception('SubIPv6Error: Unable to Substitute IPv6 Address - %s', ip)

    def parse_line(self, line, **kwargs):

        def _sub_ip(line, ip):
            new_ip = self._ip2db(ip)
            if new_ip:
                logger.debug("Obfuscating IPv6 - %s > %s", ip, new_ip)
                return line.replace(ip, new_ip)
            # it's an obfuscated IP
            return line

        if not line:
            return line

        for ip in re.findall(self.pattern, line, re.I):
            if any(re.search(_i, ip[0], re.I) for _i in self._ignore_list):
                continue
            line = _sub_ip(line, ip[0])
        return line

    def mapping(self):
        mapping = []
        for k, v in self._ipv6_db.items():
            mapping.append({'original': k, 'obfuscated': v})
        return mapping

    def generate_report(self, report_dir, archive_name):
        try:
            ip_report_file = os.path.join(report_dir, "%s-ipv6.csv" % archive_name)
            logger.info('Creating IPv6 Report - %s', ip_report_file)
            lines = ['Obfuscated IPv6,Original IPv6']
            for k, v in self._ipv6_db.items():
                lines.append('{0},{1}'.format(v, k))
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise Exception('CreateReport Error: Error Creating IPv6 Report')

        write_report(lines, ip_report_file)

        logger.info('Completed IPv6 Report.')
