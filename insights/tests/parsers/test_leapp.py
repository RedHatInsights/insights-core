import doctest

from insights.parsers import leapp
from insights.parsers.leapp import LeappReport, LeappMigrationResults
from insights.tests import context_wrap
from insights.tests.datasources.test_leapp import LEAPP_REPORT_RESULT
from insights.tests.datasources.test_leapp import MIGRATION_RESULTS_RET_1, MIGRATION_RESULTS_RET_2


def test_leapp_report():
    ret = LeappReport(context_wrap(LEAPP_REPORT_RESULT, path='insights_commands/leapp_report'))
    assert len(ret) == 4
    assert ret[0]['title'] == "Use of NFS detected. Upgrade can't proceed"
    assert 'summary' in ret[0]
    assert ret[1]['title'] == "Possible problems with remote login using root account"
    assert 'summary' in ret[1]
    assert ret[0]['remediations'][0]['context'] == "Disable NFS temporarily for the upgrade if possible."
    assert 'If you depend on remote' in ret[1]['remediations'][0]['context']
    assert 'remediations' not in ret[2]
    assert 'external' in ret[2]
    assert 'remediations' not in ret[3]
    assert 'related_resources' in ret[3]


def test_leapp_migration_results():
    ret = LeappMigrationResults(context_wrap(MIGRATION_RESULTS_RET_1, path='insights_commands/leapp_migration_results'))
    assert len(ret) == 2
    assert ret[0]['activity_ended'] == "2023-08-22T08:56:26.971009Z"
    assert ret[0]['run_id'] == "1edff870-626d-41ba-854c-8f9dc8f20dc3"
    assert ret[1]['target_os'] == "Red Hat Enterprise Linux 9.0"
    assert ret[1]['env']['LEAPP_CURRENT_PHASE'] == "InterimPreparation"


def test_c2r_migration_results():
    ret = LeappMigrationResults(context_wrap(MIGRATION_RESULTS_RET_2, path='insights_commands/leapp_migration_results'))
    assert len(ret) == 1
    assert ret[0]['activity_ended'] == "2024-03-01T07:44:15.814899Z"
    assert ret[0]['run_id'] == "null"
    assert ret[0]['target_os'] == "null"
    assert len(ret[0]['env']) == 0


def test_doc_examples():
    env = {
        'leapp_report': LeappReport(context_wrap(LEAPP_REPORT_RESULT)),
        'leapp_migration_results': LeappMigrationResults(context_wrap(MIGRATION_RESULTS_RET_1)),
    }
    failed, total = doctest.testmod(leapp, globs=env)
    assert failed == 0
