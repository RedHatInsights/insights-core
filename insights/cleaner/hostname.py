"""
Hostname Obfuscation
====================
"""

import logging
import hashlib
import os
import re
import six

from insights.cleaner.utilities import write_report

logger = logging.getLogger(__name__)


class Hostname(object):
    """
    Class for obfuscating hostname.

    .. note::

        Currently, only the system hostname will be obfuscated, see:
        - https://docs.redhat.com/en/documentation/red_hat_insights/1-latest/html/client_configuration_guide_for_red_hat_insights/assembly-client-data-obfuscation#proc-obfuscating-hostname_insights-cg-obfuscation

    """

    def __init__(self, fqdn):
        # - Hostname obfuscate information
        # - original hostname : obfuscated hostname
        self._hn_db = dict()
        fqdn_split = fqdn.split('.')
        self.pattern = (
            None
            if len(fqdn_split) <= 1
            else r'(?![\W\-\:\ \.])[a-zA-Z0-9\-\_\.]*\.{0}'.format('.'.join(fqdn_split[1:]))
        )
        self._hostname = fqdn_split[0]
        self._hn2db(fqdn)

    def _hn2db(self, hn):
        '''
        Add a hostname to DB or return an existing entry
        '''
        # Check db first
        if hn in self._hn_db:
            return self._hn_db[hn]
        # Handle domain
        hn_sp = hn.split('.')
        obf_hn = hashlib.sha1(hn_sp[0].encode('utf-8') if six.PY3 else hn_sp[0]).hexdigest()[:12]
        if len(hn_sp) > 1:
            obf_hn = '{0}.{1}'.format(obf_hn, 'example.com')
        self._hn_db[hn] = obf_hn
        return obf_hn

    def parse_line(self, line, **kwargs):
        '''
        Replace the exact hostname and all instances of the known domain with the obfuscated alternatives.
        '''
        if not line:
            return line
        try:
            if self.pattern:
                hostnames = [each for each in re.findall(self.pattern, line)]
                for hn in hostnames:
                    new_hn = self._hn2db(hn)
                    logger.debug("Obfuscating FQDN - {0} > {1}".format(hn, new_hn))
                    line = line.replace(hn, new_hn)
            # catch any non-fqdn instances of the system hostname
            if self._hostname in line:
                line = line.replace(self._hostname, self._hn2db(self._hostname))
            return line
        except Exception as e:  # pragma: no cover
            logger.warning(e)
            raise Exception('SubHostnameError: Unable to Substitute Hostname/Domainname')

    def mapping(self):
        mapping = []
        for ori, obf in self._hn_db.items():
            mapping.append({'original': ori, 'obfuscated': obf})
        return mapping

    def generate_report(self, report_dir, archive_name):
        try:
            hn_report_file = os.path.join(report_dir, "%s-hostname.csv" % archive_name)
            logger.info('Creating Hostname Report - %s', hn_report_file)
            lines = ['Obfuscated Hostname,Original Hostname']
            if self._hn_db:
                for ori, obf in self._hn_db.items():
                    lines.append('{0},{1}'.format(obf, ori))
            else:  # pragma: no cover # never false
                lines.append('None,None')
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise Exception('CreateReport Error: Error Creating Hostname Report')

        write_report(lines, hn_report_file)

        logger.info('Completed Hostname Report.')
