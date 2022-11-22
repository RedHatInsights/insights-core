"""
PcpOpenmetricsLog - file ``/var/log/pcp/pmcd/openmetrics.log``
--------------------------------------------------------------
"""
from insights.specs import Specs
from insights import LogFileOutput, parser


@parser(Specs.pcp_openmetrics_log)
class PcpOpenmetricsLog(LogFileOutput):
    """
    Parse the ``/var/log/pcp/pmcd/openmetrics.log`` log file.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput`

    Sample input::

        [Mon Jul 11 07:59:32] pmdaopenmetrics(1733) Error: cannot parse/store 55% {:
        [Mon Jul 11 07:59:32] pmdaopenmetrics(1733) Error: cannot parse/store }:
        [Mon Jul 11 07:59:32] pmdaopenmetrics(1733) Error: cannot parse/store 95% {:
        [Mon Jul 11 07:59:32] pmdaopenmetrics(1733) Error: cannot parse/store }:
        [Mon Jul 11 07:59:32] pmdaopenmetrics(1733) Error: cannot parse/store };:

    Examples:

        >>> "Error: cannot parse/store" in log
        True
        >>> len(log.get('pmdaopenmetrics')) == 5
        True
    """
    pass
