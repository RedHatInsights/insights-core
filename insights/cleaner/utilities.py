"""
Utilities for spec Cleaner
==========================
"""

import logging
import json
import os

logger = logging.getLogger(__name__)


def write_report(report, report_file, mode=0o644):
    # Get the current umask
    umask = os.umask(0o022)
    # Reset the umask
    os.umask(umask)
    try:
        with open(report_file, 'w') as fp:
            if isinstance(report, dict):
                json.dump(report, fp)
            elif isinstance(report, list):
                for line in report:
                    fp.write("{0}\n".format(line))
        # Change the file mode per the current umask
        os.chmod(report_file, mode & ~umask)
    except (IOError, OSError) as e:  # pragma: no cover
        logger.error('Could not write to %s: %s', report_file, str(e))
