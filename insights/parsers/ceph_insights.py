"""
ceph_insights - command ``ceph insights``
=========================================
"""
import json
import re
from .. import CommandParser, parser
from insights.specs import Specs


@parser(Specs.ceph_insights)
class CephInsights(CommandParser):
    """
    Parse the output of the ``ceph insights`` command.

    Attributes:
        version (dict): version information of the Ceph cluster.
        data (dict): a dictionary of the parsed output.

    The ``data`` attribute is a dictionary containing the parsed output of the
    ``ceph insights`` command. The following are available in ``data``:

    * ``crashes`` - summary of daemon crashes for the past 24 hours
    * ``health`` - the current and historical (past 24 hours) health checks
    * ``config`` - cluster and daemon configuration settings
    * ``osd_dump`` - osd and pool information
    * ``df`` - storage usage statistics
    * ``osd_tree`` - osd topology
    * ``fs_map`` - file system map
    * ``crush_map`` - the CRUSH map
    * ``mon_map`` - monitor map
    * ``service_map`` - service map
    * ``manager_map`` - manager map
    * ``mon_status`` - monitor status
    * ``pg_summary`` - placement group summary
    * ``osd_metadata`` - per-OSD metadata
    * ``version`` - ceph software version
    * ``errors`` - any errors encountered collecting this data

    The ``version`` attribute contains a normalized view of ``self.data["version"]``.

    Examples:
        >>> ceph_insights.version["release"] == 14
        True
        >>> ceph_insights.version["major"] == 0
        True
        >>> ceph_insights.version["minor"] == 0
        True
        >>> isinstance(ceph_insights.data["crashes"], dict)
        True
        >>> isinstance(ceph_insights.data["health"], dict)
        True
    """
    IGNORE_RE = [
         "\*\*\* DEVELOPER MODE",
         "\d+-\d+-\d+.+WARNING: all dangerous"
    ]

    bad_lines = [
        "module 'insights' is not enabled",
        "no valid command found"
    ]

    def __init__(self, *args, **kwargs):
        kwargs.update(dict(extra_bad_lines=self.bad_lines))
        super(CephInsights, self).__init__(*args, **kwargs)

    def _sanitize_content(self, content):
        """Remove lines matching IGNORE_RE at start of content"""
        slice_point = 0
        ignore_re = re.compile('|'.join(CephInsights.IGNORE_RE))
        for line in content:
            if not line or ignore_re.match(line):
                slice_point += 1
                continue
            break
        return content[slice_point:]

    def _parse_version(self):
        """
        Add a Ceph version property as a dictionary with the keys "release",
        "major", "minor" containing numeric values, and the key "full" with the
        full version string. If Ceph is not compiled with verison information
        (this should never be the case in a production system), then "release",
        "major", and "minor" are set to None.
        """
        self.version = {
            "release": None,
            "major": None,
            "minor": None
        }
        self.version.update(self.data["version"])

    def parse_content(self, content):
        content = self._sanitize_content(content)
        self.data = json.loads(''.join(content))
        self._parse_version()
