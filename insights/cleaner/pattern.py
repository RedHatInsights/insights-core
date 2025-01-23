"""
Pattern Redaction
=================
"""

import logging
import re

logger = logging.getLogger(__name__)


class Pattern(object):
    """
    Class for redacting "patterns" configured in "file-content.redaction.yaml".
    """

    def __init__(self, exclude, regex=False):
        self._exclude = exclude or []
        self._regex = regex

    def parse_line(self, line, **kwargs):
        # redact line per the file-content-redaction.yaml
        if not line:
            return line
        # patterns removal
        find = re.search if self._regex else lambda x, y: x in y
        if any(find(pat, line) for pat in self._exclude):
            logger.debug("Pattern matched, removing line: %s" % line.strip())
            # patterns found, remove it
            return None
        return line

    def generate_report(self, report_dir, archive_name):
        pass  # pragma: no cover
