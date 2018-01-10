"""
nova_log - files ``/var/log/nova/*.log``
========================================
This module contains classes to parse logs under ``/var/log/nova/``
"""
from .. import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.nova_api_log)
class NovaApiLog(LogFileOutput):
    """Class for parsing the ``/var/log/nova/nova-api.log`` file.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput`
    """
    pass


@parser(Specs.nova_compute_log)
class NovaComputeLog(LogFileOutput):
    """Class for parsing the ``/var/log/nova/nova-compute.log`` file.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput`
    """
    pass
