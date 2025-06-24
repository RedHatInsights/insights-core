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
            for a_key in list(allowlist.keys()):  # copy keys to avoid RuntimeError
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

    @staticmethod
    def filter_content(lines, allowlist):
        """
        Filter content based on allowlist.

        When a key of allowlist is found in a line, it is added to the result
        list. The key is removed from the allowlist when enough lines
        containing the key were found.
        When the allowlist is empty, an empty result is returned.

        The lines are processed in reverse order.   But the processed result
        is returned in the original order.

        :param lines: list of lines
        :param allowlist: dictionary of allowlist
        :return: list of lines
        """
        allowlist = dict(allowlist)  # copy it to avoid write back
        result = []
        for idx in range(len(lines) - 1, -1, -1):
            for a_key in list(allowlist.keys()):  # copy keys to avoid RuntimeError
                if a_key in lines[idx]:
                    allowlist[a_key] -= 1
                    # stop checking it when enough lines contain the key were found
                    allowlist.pop(a_key) if allowlist[a_key] == 0 else None
                    result.append(lines[idx])
                    # stop checking other keys when one key is found
                    # it's sometimes not fair to other keys, but it's
                    # the best we can do for performance
                    break
        # Return the result in right order
        result.reverse()
        return result
