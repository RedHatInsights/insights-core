import doctest

from insights.parsers import leapp
from insights.parsers.leapp import LeappReport
from insights.tests import context_wrap
from insights.tests.datasources.test_leapp import RESULT


def test_leapp():
    ret = LeappReport(context_wrap(RESULT, path='insights_commands/leapp_report'))
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


def test_doc_examples():
    env = {'leapp_report': LeappReport(context_wrap(RESULT))}
    failed, total = doctest.testmod(leapp, globs=env)
    assert failed == 0
