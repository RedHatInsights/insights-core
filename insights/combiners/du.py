"""
Disk Usage
==========

Combiners for gathering information from du parsers.
"""

from insights import combiner
from insights.parsers.du import DiskUsageDir


@combiner(DiskUsageDir)
class DiskUsageDirs(dict):
    """
    Combiner for the :class:`insights.parsers.du.DiskUsageDir` parser.

    The parser is multioutput, one parser instance for each directory disk
    usage. This combiner puts all of them back together and presents them as a
    dict where the keys are the directory names and the space usage are the
    values.

    Sample input data for du commands as parsed by the parsers::

        # Output of the command:
        # /bin/du -s -k /var/log
        553500	/var/log

        # Output of the command:
        # /bin/du -s -k /var/lib/pgsql
        519228	/var/lib/pgsql

    Examples:
        >>> type(disk_usage_dirs)
        <class 'insights.combiners.du.DiskUsageDirs'>
        >>> sorted(disk_usage_dirs.keys())
        ['/var/lib/pgsql', '/var/log']
        >>> disk_usage_dirs['/var/lib/pgsql']
        519228
    """
    def __init__(self, du_dirs):
        super(DiskUsageDirs, self).__init__()
        for du in du_dirs:
            self.update(du)
