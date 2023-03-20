import doctest

from insights.parsers import mssql_api_assessment
from insights.parsers.mssql_api_assessment import MssqlApiAssessment, ContainerMssqlApiAssessment
from insights.tests import context_wrap

API_OUTPUT = """
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
""".strip()


def test_mssql_api_assessment():
    ret = MssqlApiAssessment(context_wrap(API_OUTPUT))
    assert ret[0]["Severity"] == "Information"
    assert ret[0]["TargetName"] == "ceph4-mon"
    assert ret[0]["CheckId"] == "TF174"
    assert ret[0]["Message"] == "Enable trace flag 174 to increase plan cache bucket count"


def test_mssql_api_assessment_container():
    container_ret = ContainerMssqlApiAssessment(
        context_wrap(
            API_OUTPUT,
            container_id='2869b4e2541c',
            image='registry.access.redhat.com/ubi8/nginx-120',
            engine='podman',
        )
    )
    assert container_ret.container_id == "2869b4e2541c"
    assert container_ret[0]["Severity"] == "Information"
    assert container_ret[0]["TargetName"] == "ceph4-mon"
    assert container_ret[0]["CheckId"] == "TF174"
    assert container_ret[0]["Message"] == "Enable trace flag 174 to increase plan cache bucket count"


def test_mssql_api_assessment_doc_examples():
    env = {
        'mssql_api_assessment_output': MssqlApiAssessment(context_wrap(API_OUTPUT)),
        'container_mssql_api_assessment_output': ContainerMssqlApiAssessment(
            context_wrap(
                API_OUTPUT,
                container_id='2869b4e2541c',
                image='registry.access.redhat.com/ubi8/nginx-120',
                engine='podman',
            )
        )
    }
    failed, total = doctest.testmod(mssql_api_assessment, globs=env)
    assert failed == 0
