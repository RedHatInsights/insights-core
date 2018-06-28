"""
RHV Log Collector Analyzer
==========================

RHV Log Collector Analyzer is a tool that analyze RHV sosreports
and live systems.

This module provides processing for the output of
rhv-log-collector-analyzer --json which will be running
in a live system to detect possible issues.
"""

from .. import JSONParser, parser, CommandParser
from insights.specs import Specs


@parser(Specs.rhv_log_collector_analyzer)
class RhvLogCollectorJson(CommandParser, JSONParser):
    """
    Class to parse the output of ``rhv-log-collector-analyzer --json``.
    """
    pass
