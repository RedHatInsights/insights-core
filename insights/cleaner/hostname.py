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
        self._fqdn = fqdn
        name_list = self._fqdn.split('.')
        self._hostname = name_list[0]
        self._domain = None if len(name_list) <= 1 else '.'.join(name_list[1:])

        # - Hostname obfuscate information
        self._hn_db = dict()  # hostname database
        self._hostname_count = 0
        self._obfuscated_domain = 'example.com'

        # - Domain name obfuscate information
        self._dn_db = dict()  # domain name database
        self._domain_count = 0

        self._domains2db()
        self._obfuscated_fqdn = '{0}.example.com'.format(
            hashlib.sha1(self._fqdn.encode('utf-8') if six.PY3 else self._fqdn).hexdigest()[:12]
        )
        self._hostname_count += 1
        self._hn_db[self._obfuscated_fqdn] = self._fqdn

    def _domains2db(self):
        # adds any additional domainnames to the domain database to be searched for
        try:
            # we will add the root domain for an FQDN as well.
            if self._domain is not None:
                self._dn_db[self._obfuscated_domain] = self._domain
                logger.debug(
                    "Obfuscated Domain Created - %s -> %s" % (self._domain, self._obfuscated_domain)
                )

            self._domain_count = len(self._dn_db)
            return True
        except Exception as e:  # pragma: no cover
            logger.warning(e)

    def _hn2db(self, hn):
        '''
        This will add a hostname for a hostname for an included domain or return an existing entry
        '''
        db = self._hn_db
        hn_found = False
        for k, v in db.items():
            if v == hn:  # the hostname is in the database
                ret_hn = k
                hn_found = True
        if hn_found:
            return ret_hn
        else:
            # we have a new hostname, so we increment the counter to get the host ID number
            self._hostname_count += 1
            o_domain = self._obfuscated_domain
            for od, d in self._dn_db.items():
                if d in hn:  # pragma: no cover # never false
                    o_domain = od
            new_hn = "host%s.%s" % (self._hostname_count, o_domain)
            self._hn_db[new_hn] = hn
            return new_hn

    def parse_line(self, line, **kwargs):
        '''
        This will replace the exact hostname and all instances of the domain name with the obfuscated alternatives.
        Example:
        '''
        if not line:
            return line
        try:
            for od, d in self._dn_db.items():
                # regex = re.compile(r'\w*\.%s' % d)
                regex = re.compile(r'(?![\W\-\:\ \.])[a-zA-Z0-9\-\_\.]*\.%s' % d)
                hostnames = [each for each in regex.findall(line)]
                if len(hostnames) > 0:
                    for hn in hostnames:
                        new_hn = self._hn2db(hn)
                        logger.debug("Obfuscating FQDN - %s > %s", hn, new_hn)
                        line = line.replace(hn, new_hn)
            # catch any non-fqdn instances of the system hostname
            line = line.replace(self._hostname, self._hn2db(self._fqdn))
            return line
        except Exception as e:  # pragma: no cover
            logger.warning(e)
            raise Exception('SubHostnameError: Unable to Substitute Hostname/Domainname')

    def mapping(self):
        mapping = []
        for k, v in self._hn_db.items():
            mapping.append({'original': v, 'obfuscated': k})
        return mapping

    def generate_report(self, report_dir, archive_name):
        try:
            hn_report_file = os.path.join(report_dir, "%s-hostname.csv" % archive_name)
            logger.info('Creating Hostname Report - %s', hn_report_file)
            lines = ['Obfuscated Hostname,Original Hostname']
            if self._hostname_count > 0:
                for k, v in self._hn_db.items():
                    lines.append('{0},{1}'.format(k, v))
            else:  # pragma: no cover # never false
                lines.append('None,None')
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise Exception('CreateReport Error: Error Creating Hostname Report')

        write_report(lines, hn_report_file)

        logger.info('Completed Hostname Report.')
