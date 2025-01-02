"""
Pattern redaction
=================
"""

import logging
import re

logger = logging.getLogger(__name__)


class Pattern(object):
    def __init__(self, exclude, regex=False):
        self.exclude = exclude or []
        self.regex = regex

    def parse_line(self, line, **kwargs):
        # redact line per the file-content-redaction.yaml
        if not line:
            return line
        # patterns removal
        find = re.search if self.regex else lambda x, y: x in y
        if any(find(pat, line) for pat in self.exclude):
            logger.debug("Pattern matched, removing line: %s" % line.strip())
            # patterns found, remove it
            return None
        return line

    def generate_report(self, report_dir, archive_name):
        pass  # pragma: no cover
