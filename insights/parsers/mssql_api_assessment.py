"""
MssqlApiAssessment - file ``/var/opt/mssql/log/assessments/assessment-latest``
==============================================================================

Parsers contains in this module are:

MssqlApiAssessment - file ``/var/opt/mssql/log/assessments/assessment-latest``
"""

from insights import JSONParser, parser
from insights.core import ContainerParser
from insights.specs import Specs


@parser(Specs.mssql_api_assessment)
class MssqlApiAssessment(JSONParser):
    """
    Parses the file: ``/var/opt/mssql/log/assessments/assessment-latest``

    Sample content of the file::

        [
          {
            "Timestamp": "2021-05-05T21:51:55.2317511-04:00",
            "Severity": "Information",
            "TargetType": "Server",
            "TargetName": "ceph4-mon",
            "TargetPath": "Server[@Name='ceph4-mon']",
            "CheckId": "TF174",
            "CheckName": "TF 174 increases plan cache bucket count",
            "Message": "Enable trace flag 174 to increase plan cache bucket count",
            "RulesetName": "Microsoft ruleset",
            "RulesetVersion": "1.0.305",
            "HelpLink": "https://docs.microsoft.com/sql/t-sql/database-console-commands/dbcc-traceon-trace-flags-transact-sql"
          },
          {
            "Timestamp": "2021-05-05T21:51:55.2323431-04:00",
            "Severity": "Information",
            "TargetType": "Server",
            "TargetName": "ceph4-mon",
            "TargetPath": "Server[@Name='ceph4-mon']",
            "CheckId": "TF834",
            "CheckName": "TF 834 enables large-page allocations",
            "Message": "Enable trace flag 834 to use large-page allocations to improve analytical and data warehousing workloads",
            "RulesetName": "Microsoft ruleset",
            "RulesetVersion": "1.0.305",
            "HelpLink": "https://support.microsoft.com/kb/3210239"
          }
        ]

    Examples:
        >>> type(mssql_api_assessment_output)
        <class 'insights.parsers.mssql_api_assessment.MssqlApiAssessment'>
        >>> mssql_api_assessment_output[0]["Severity"] == 'Information'
        True
    """
    pass


@parser(Specs.container_mssql_api_assessment)
class ContainerMssqlApiAssessment(ContainerParser, MssqlApiAssessment):
    """
    Parses the file: ``/var/opt/mssql/log/assessments/assessment-latest`` from the container

    Sample content of the file::

        [
          {
            "Timestamp": "2021-05-05T21:51:55.2317511-04:00",
            "Severity": "Information",
            "TargetType": "Server",
            "TargetName": "ceph4-mon",
            "TargetPath": "Server[@Name='ceph4-mon']",
            "CheckId": "TF174",
            "CheckName": "TF 174 increases plan cache bucket count",
            "Message": "Enable trace flag 174 to increase plan cache bucket count",
            "RulesetName": "Microsoft ruleset",
            "RulesetVersion": "1.0.305",
            "HelpLink": "https://docs.microsoft.com/sql/t-sql/database-console-commands/dbcc-traceon-trace-flags-transact-sql"
          },
          {
            "Timestamp": "2021-05-05T21:51:55.2323431-04:00",
            "Severity": "Information",
            "TargetType": "Server",
            "TargetName": "ceph4-mon",
            "TargetPath": "Server[@Name='ceph4-mon']",
            "CheckId": "TF834",
            "CheckName": "TF 834 enables large-page allocations",
            "Message": "Enable trace flag 834 to use large-page allocations to improve analytical and data warehousing workloads",
            "RulesetName": "Microsoft ruleset",
            "RulesetVersion": "1.0.305",
            "HelpLink": "https://support.microsoft.com/kb/3210239"
          }
        ]

    Examples:
        >>> type(container_mssql_api_assessment_output)
        <class 'insights.parsers.mssql_api_assessment.ContainerMssqlApiAssessment'>
        >>> container_mssql_api_assessment_output.container_id
        '2869b4e2541c'
        >>> container_mssql_api_assessment_output.image
        'registry.access.redhat.com/ubi8/nginx-120'
        >>> container_mssql_api_assessment_output[0]["Severity"] == 'Information'
        True
    """
    pass
