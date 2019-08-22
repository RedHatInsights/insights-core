import os
import sys
from insights import run, make_fail, make_pass
from insights.core import dr
from insights.plugins import always_fires, never_fires
from insights.specs import Specs
from mock import patch
from insights.tests.spec_tests import report_multioutput, report_nonexistent, report_raw


class stage(dr.ComponentType):
    pass


@stage("dep1")
def stage1(dep1):
    return "stage1"


@stage("dep2")
def stage2(dep2):
    return "stage2"


@stage("common")
def stage3(common):
    return common


@stage("common")
def stage4(common):
    return common


def test_run():
    broker = dr.Broker()
    broker["common"] = 3
    graph = dr.get_dependency_graph(stage3)
    graph.update(dr.get_dependency_graph(stage4))
    broker = dr.run(graph, broker)

    assert stage3 in broker.instances
    assert broker[stage3] == 3

    assert stage4 in broker.instances
    assert broker[stage4] == 3


def test_run_incremental():
    broker = dr.Broker()
    broker["dep1"] = 1
    broker["dep2"] = 2
    broker["common"] = 3

    graph = dr.get_dependency_graph(stage1)
    graph.update(dr.get_dependency_graph(stage2))
    graph.update(dr.get_dependency_graph(stage3))
    graph.update(dr.get_dependency_graph(stage4))

    brokers = list(dr.run_incremental(graph, broker))
    assert len(brokers) == 3


ALWAYS_FIRES_RESULT = make_pass("ALWAYS_FIRES", kernel="this is junk")
NEVER_FIRES_RESULT = {
    'rule_fqdn': 'insights.plugins.never_fires.report',
    'reason': 'MISSING_REQUIREMENTS',
    'details': "All: ['insights.plugins.never_fires.thing'] Any: ",
    'type': 'skip'}
REDHAT_RELEASE = "Red Hat Enterprise Linux Server release 7.3 (Maipo)"
UNAME = "Linux test.redhat.com 3.10.0-514.el7.x86_64 #1 SMP Wed Oct 19 11:24:13 EDT 2016 x86_64 x86_64 x86_64 GNU/Linux"


def test_run_command(tmpdir):

    d = tmpdir / "etc"
    d.mkdir()
    p = d / "redhat-release"
    p.write(REDHAT_RELEASE)
    g = tmpdir / "insights_commands"
    g.mkdir()
    r = g / "uname_-a"
    r.write(UNAME)

    broker = run([always_fires.report, never_fires.report])
    assert broker is not None
    assert always_fires.report in broker
    assert never_fires.report in broker
    assert broker[always_fires.report] == ALWAYS_FIRES_RESULT
    assert broker[never_fires.report] == NEVER_FIRES_RESULT

    broker = run([Specs.redhat_release, always_fires.report, never_fires.report], root=tmpdir.strpath)
    assert broker is not None
    assert always_fires.report in broker
    assert never_fires.report in broker
    assert broker[always_fires.report] == ALWAYS_FIRES_RESULT
    assert broker[never_fires.report] == NEVER_FIRES_RESULT
    assert Specs.redhat_release in broker
    assert broker[Specs.redhat_release].content == [REDHAT_RELEASE]

    testargs = ["insights-run", "-p", "insights.plugins"]
    with patch.object(sys, 'argv', testargs):
        broker = run(print_summary=True)
        assert broker is not None
        assert always_fires.report in broker
        assert never_fires.report in broker
        assert broker[always_fires.report] == ALWAYS_FIRES_RESULT
        assert broker[never_fires.report] == NEVER_FIRES_RESULT

    testargs = ["insights-run", "-p", "insights.plugins", tmpdir.strpath]
    with patch.object(sys, 'argv', testargs):
        broker = run(print_summary=True)
        assert broker is not None
        assert always_fires.report in broker
        assert never_fires.report in broker
        assert broker[always_fires.report] == ALWAYS_FIRES_RESULT
        assert broker[never_fires.report] == NEVER_FIRES_RESULT
        assert Specs.uname in broker
        assert broker[Specs.uname].content == [UNAME]


SAMPLE_LOG = """
1 line one
2 line two
""".strip()


def test_bare_files(tmpdir):
    d = tmpdir / "bare"
    d.mkdir()
    p = d / 'sample.log'
    p.write(SAMPLE_LOG)
    data = [l.strip() for l in SAMPLE_LOG.splitlines()]

    testargs = [
        "insights-run",
        "-t", "-m",
        "-b", 'insights.tests.spec_tests.TSpecs.sample_multioutput_file={fname}'.format(fname=os.path.join(tmpdir.strpath, 'bare', 'sample.log')),
        "-p", "insights.tests.spec_tests"]
    with patch.object(sys, 'argv', testargs):
        broker = run(print_summary=True)
        assert broker is not None
        assert report_multioutput in broker
        assert broker[report_multioutput] == make_fail('MO_SPEC', data=data, number=1)

    testargs = [
        "insights-run",
        "-t", "-m",
        "-b", 'insights.tests.spec_tests.TSpecs.sample_nonexistent={fname}'.format(fname=os.path.join(tmpdir.strpath, 'bare', 'sample.log')),
        "-p", "insights.tests.spec_tests"]
    with patch.object(sys, 'argv', testargs):
        broker = run(print_summary=True)
        assert broker is not None
        assert report_nonexistent in broker
        assert broker[report_nonexistent] == make_fail('NE_SPEC', data=data)

    testargs = [
        "insights-run",
        "-t", "-m",
        "-b", 'insights.tests.spec_tests.TSpecs.sample_raw_file={fname}'.format(fname=os.path.join(tmpdir.strpath, 'bare', 'sample.log')),
        "-p", "insights.tests.spec_tests"]
    with patch.object(sys, 'argv', testargs):
        broker = run(print_summary=True)
        assert broker is not None
        assert report_raw in broker
        with open(os.path.join(tmpdir.strpath, 'bare', 'sample.log'), 'rb') as fh:
            data_b = fh.read()
        assert broker[report_raw] == make_fail('RA_SPEC', data=data_b)
