"""
Password Replacement
====================

"""

import logging
import re

logger = logging.getLogger(__name__)

DEFAULT_PASSWORD_REGEXS = [
    r"(password[a-zA-Z0-9_]*)(\s*\:\s*\"*\s*|\s*\"*\s*=\s*\"\s*|\s*=+\s*|\s*--md5+\s*|\s*)([a-zA-Z0-9_!@#$%^&*()+=/-]+)",
    r"(password[a-zA-Z0-9_]*)(\s*\*+\s+)(.+)",
]


class Password(object):
    """
    Class to replace the possible password to "********".

    .. note::

        Currently, the "passowrd" is the only keyword to check for potential
        Password.
    """

    def parse_line(self, line, **kwargs):
        if not line:
            return line
        # password obfuscation
        for regex in DEFAULT_PASSWORD_REGEXS:
            tmp_line = line
            line = re.sub(regex, r"\1\2********", tmp_line)
            if line != tmp_line:
                break
        return line

    def generate_report(self, report_dir, archive_name):
        pass
