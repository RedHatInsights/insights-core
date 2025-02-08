"""
Filtering
=========
"""

import logging

logger = logging.getLogger(__name__)


class AllowFilter(object):
    """
    Class for filtering per allow list.
    """

    def parse_line(self, line, **kwargs):
        # filter line as per the allow list specified by plugins
        if not line:
            return line
        allowlist = kwargs.get('allowlist', {})
        if allowlist:
            for a_key in list(allowlist.keys()):
                # keep line when any filter match
                # FIXME:
                # Considering performance, didn't handle multiple filters in one same line
                if a_key in line:
                    allowlist[a_key] -= 1
                    # stop checking it when enough lines contain the key were found
                    allowlist.pop(a_key) if allowlist[a_key] == 0 else None
                    return line
        # discard line when none filters found

    def generate_report(self, report_dir, archive_name):
        pass  # pragma: no cover
