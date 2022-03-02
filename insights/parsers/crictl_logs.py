"""
CrictlLogs - commands `crictl logs -t <container's_ID>``
========================================================
"""

from insights.core import LogFileOutput
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.crictl_logs)
class CrictlLogs(LogFileOutput):
    """
    Class for parsing the output of commands ``crictl logs -t <container's_ID>``.

    Sample input data looks like::

        2021-12-21T11:12:45.854971114+01:00 Successfully copied files in /usr/src/multus-cni/rhel7/bin/ to /host/opt/cni/bin/
        2021-12-21T11:12:45.995998017+01:00 2021-12-21T10:12:45+00:00 WARN: {unknown parameter "-"}
        2021-12-21T11:12:46.008998978+01:00 2021-12-21T10:12:46+00:00 Entrypoint skipped copying Multus binary.
        2021-12-21T11:12:46.081427544+01:00 2021-12-21T10:12:46+00:00 Attempting to find master plugin configuration, attempt 0

    Note:
        Please refer to its super-class :class:`insights.core.LogFileOutput`.

    Examples:
        >>> len(logs.get('skipped copying Multus binary'))
        1
    """
    pass
