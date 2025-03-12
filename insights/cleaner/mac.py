"""
MAC Obfuscation
===============
"""

import hashlib
import logging
import os
import re
import six

from insights.cleaner.utilities import write_report

logger = logging.getLogger(__name__)


class Mac(object):
    """
    Class for obfuscating MAC addresses
    """

    def __init__(self):
        self._mac_db = dict()  # MAC database
        # Ignore list for MAC addresses
        # - 00:00:00:00:00:00
        # - FF:FF:FF:FF:FF:FF
        self._ignore_list = [r'\b(?:(?:00:){5}00|(?:ff:){5}ff)\b']
        # MAC address patterns
        self.pattern = r'(?<![0-9a-fA-F:-])([0-9a-fA-F]{2}([:-])(?:[0-9a-fA-F]{2}\2){4}[0-9a-fA-F]{2})(?![0-9a-fA-F:-])'

    def _mac2db(self, mac):
        '''
        Add an MAC address to MAC database and return obfuscated address.

        FORMAT:
        {$original_mac:, $obfuscated_mac}
        '''

        def obfuscate_hex(_hex, lower=True):
            __hex = _hex.encode('utf-8') if six.PY3 else _hex
            new_hex = hashlib.sha1(__hex.lower()).hexdigest()[: len(__hex)]
            return new_hex if lower else new_hex.upper()

        try:
            if mac in self._mac_db:
                return self._mac_db[mac]
            if mac in self._mac_db.values():  # pragma: no cover
                # avoid nested obfuscating
                return None
            lower = not mac.isupper()
            sep = '-' if '-' in mac else ':'
            self._mac_db[mac] = sep.join(obfuscate_hex(h, lower) for h in mac.split(sep))
            return self._mac_db[mac]
        except Exception as e:  # pragma: no cover
            logger.warning(e)
            raise Exception('SubMacError: Unable to Substitute MAC Addr - %s', mac)

    def parse_line(self, line, **kwargs):

        def _sub_mac(line, mac):
            new_mac = self._mac2db(mac)
            if new_mac:
                logger.debug("Obfuscating MAC Addr - %s > %s", mac, new_mac)
                return line.replace(mac, new_mac)
            # it's an obfuscated MAC address
            return line

        if not line:
            return line

        for mac in re.findall(self.pattern, line, re.I):
            if not any(re.search(_i, mac[0], re.I) for _i in self._ignore_list):
                line = _sub_mac(line, mac[0])

        return line

    def mapping(self):
        mapping = []
        for k, v in self._mac_db.items():
            mapping.append({'original': k, 'obfuscated': v})
        return mapping

    def generate_report(self, report_dir, archive_name):
        try:
            mac_report_file = os.path.join(report_dir, "%s-mac.csv" % archive_name)
            logger.info('Creating MAC addr Report - %s', mac_report_file)
            lines = ['Obfuscated MAC,Original MAC']
            for k, v in self._mac_db.items():
                lines.append('{0},{1}'.format(v, k))
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise Exception('Error: Cannot creat MAC addr obfuscate report')

        write_report(lines, mac_report_file)

        logger.info('Completed MAC addr Report.')
