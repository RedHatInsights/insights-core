"""
Leapp
=====
Parsers for parsing output of the
:py:mod:`insights.specs.datasources.leapp.leapp_report` datasource.

LeappMigrationResults - based on ``/etc/migration-results``
-----------------------------------------------------------

LeappReport - based on ``/var/log/leapp/leapp-report.json``
-----------------------------------------------------------
"""
import json

from insights.core import Parser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.leapp_migration_results)
class LeappMigrationResults(Parser, list):
    """
    Class for parsing the
    :py:mod:`insights.specs.datasources.leapp.migration_results` datasource.

    Examples:
        >>> type(leapp_migration_results)
        <class 'insights.parsers.leapp.LeappMigrationResults'>
        >>> len(leapp_migration_results)
        2
        >>> leapp_migration_results[0]['run_id'] == '1edff870-626d-41ba-854c-8f9dc8f20dc3'
        True
    """
    def parse_content(self, content):
        # content will never be empty if the parser got triggered
        self.extend(json.loads(''.join(content)))


@parser(Specs.leapp_report)
class LeappReport(Parser, list):
    """
    Class for parsing the
    :py:mod:`insights.specs.datasources.leapp.leapp_report` datasource.

    Examples:
        >>> type(leapp_report)
        <class 'insights.parsers.leapp.LeappReport'>
        >>> 'inhibitor' in leapp_report[0]['groups']
        True
        >>> "Use of NFS detected. " in leapp_report[0]['title']
        True
    """
    def parse_content(self, content):
        # content will never be empty if the parser got triggered
        self.extend(json.loads(''.join(content)))
