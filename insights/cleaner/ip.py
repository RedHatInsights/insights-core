"""
IP Obfuscation
==============
The following cleaners are included in this module:

IPv4 Obfuscation
----------------

IPv6 Obfuscation
----------------

"""

import logging
import os
import re
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
            logger.debug("Obfuscating IP - %s > %s", ip, new_ip)
            return line.replace(ip, new_ip)

        def _sub_ip_keep_width(line, ip):
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
            pattern = r"(((\b25[0-5]|\b2[0-4][0-9]|\b1[0-9][0-9]|\b[1-9][0-9]|\b[1-9]))(\.(\b25[0-5]|\b2[0-4][0-9]|\b1[0-9][0-9]|\b[1-9][0-9]|\b[0-9])){3})"
            ips = [each[0] for each in re.findall(pattern, line)]
            if len(ips) > 0:
                for ip in sorted(ips, key=len, reverse=True):
                    if ip not in self._ignore_list and ip in line:
                        if kwargs.get('width', False):
                            line = _sub_ip_keep_width(line, ip)
                        else:
                            line = _sub_ip(line, ip)
            return line
        except Exception as e:  # pragma: no cover
            logger.warning(e)
            raise Exception('SubIPError: Unable to Substitute IP Address - %s', ips)

    def mapping(self):
        mapping = []
        for k, v in self._ip_db.items():
            mapping.append({'original': self._int2ip(v), 'obfuscated': self._int2ip(k)})
        return mapping

    def generate_report(self, report_dir, archive_name):
        try:
            ip_report_file = os.path.join(report_dir, "%s-ip.csv" % archive_name)
            logger.info('Creating IP Report - %s', ip_report_file)
            lines = ['Obfuscated IP,Original IP']
            for k, v in self._ip_db.items():
                lines.append('{0},{1}'.format(self._int2ip(k), self._int2ip(v)))
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise Exception('CreateReport Error: Error Creating IP Report')

        write_report(lines, ip_report_file)

        logger.info('Completed IP Report.')


# TODO
class IPv6(object):
    """
    Class for obfuscating IPv6.
    """

    pass
