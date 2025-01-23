"""
Keyword Replacement
===================
"""

import logging
import os

from insights.cleaner.utilities import write_report

logger = logging.getLogger(__name__)


class Keyword(object):
    """
    Class to replace the keyword specified by users to "keyword#"
    """

    def __init__(self, keywords=None):
        # - Keyword replacement information
        self._kw_key = "keyword"
        self._kw_db = dict()  # keyword database
        self._keywords2db(keywords)
        self._obfuscated = set()  # keywords that have been replaced

    def _keywords2db(self, keywords):
        # processes optional keywords to add to be obfuscated
        try:
            if keywords:
                k_count = 0
                for keyword in keywords:
                    keyword = keyword.strip()
                    o_kw = "{0}{1}".format(self._kw_key, k_count)
                    self._kw_db[keyword] = o_kw
                    logger.debug("Added Obfuscated Keyword - %s", o_kw)
                    k_count += 1
                logger.debug("Added All keyword Contents from Customer's configuration")
        except Exception as e:  # pragma: no cover
            logger.warning(e)

    def parse_line(self, line, **kwargs):
        if not line:
            return line
        for k, v in self._kw_db.items():
            if k in line:
                logger.debug("Replacing Keyword - %s > %s", k, v)
                line = line.replace(k, v)
                self._obfuscated.add(k)
        return line

    def mapping(self):
        mapping = []
        for k in self._obfuscated:
            mapping.append({'original': k, 'obfuscated': self._kw_db[k]})
        return mapping

    def generate_report(self, report_dir, archive_name):
        try:
            kw_report_file = os.path.join(report_dir, "%s-keyword.csv" % archive_name)
            logger.info('Creating Keyword Report - %s', kw_report_file)
            lines = ['Replaced Keyword,Original Keyword']
            for k in self._obfuscated:
                lines.append('{0},{1}'.format(k, self._kw_db[k]))
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise Exception('CreateReport Error: Error Creating Keyword Report')
        write_report(lines, kw_report_file)
        logger.info('Completed Keyword Report.')
