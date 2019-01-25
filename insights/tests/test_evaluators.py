from insights import dr, rule, make_fail, make_pass, make_fingerprint
from insights.core.plugins import component, Response
from insights.core.evaluators import InsightsEvaluator, SingleEvaluator
from insights.combiners.hostname import hostname
from insights.specs import Specs
from insights.tests import context_wrap


class make_unsure(Response):
    """
    Show that anybody can make a Response subclass for rules to return
    and have it included in the evaluator results.
    """
    response_type = "unsure"
    key_name = "unsure_key"


@component()
def one():
    return 1


@component()
def two():
    return 2


@component()
def boom():
    raise Exception()


@rule()
def report_pass():
    return make_pass("PASS")


@rule()
def report_fail():
    return make_fail("FAIL")


@rule()
def report_fingerprint():
    return make_fingerprint("FINGERPRINT")


@rule()
def report_unsure():
    return make_unsure("unsure")


@rule(boom)
def report_boom():
    pass


@rule(one, two)
def report(a, b):
    return make_fail("FAIL2", a=a, b=b, c=a + b)


components = [
    hostname,
    Specs.redhat_release,
    Specs.machine_id,
    one,
    two,
    boom,
    report_pass,
    report_fail,
    report_fingerprint,
    report_unsure,
    report_boom,
    report
]


def test_single_evaluator():
    broker = dr.Broker()
    e = SingleEvaluator(broker)
    graph = dr.get_dependency_graph(report)
    result1 = e.process(graph)

    broker = dr.Broker()
    with SingleEvaluator(broker) as e:
        dr.run(report, broker=broker)
        result2 = e.get_response()
        assert result1 == result2


def test_insights_evaluator():
    broker = dr.Broker()
    e = InsightsEvaluator(broker)
    graph = dr.get_dependency_graph(report)
    result1 = e.process(graph)

    broker = dr.Broker()
    with InsightsEvaluator(broker) as e:
        dr.run(report, broker=broker)
        result2 = e.get_response()
        assert result1 == result2


def test_insights_evaluator_attrs_serial():
    broker = dr.Broker()
    broker[Specs.hostname] = context_wrap("www.example.com")
    broker[Specs.machine_id] = context_wrap("12345")
    broker[Specs.redhat_release] = context_wrap("Red Hat Enterprise Linux Server release 7.4 (Maipo)")
    with InsightsEvaluator(broker) as e:
        dr.run(components, broker=broker)
        result = e.get_response()
        assert result["system"]["hostname"] == "www.example.com"
        assert result["system"]["system_id"] == "12345"
        assert result["system"]["metadata"]["release"] == "Red Hat Enterprise Linux Server release 7.4 (Maipo)"


def test_insights_evaluator_attrs_serial_process():
    broker = dr.Broker()
    broker[Specs.hostname] = context_wrap("www.example.com")
    broker[Specs.machine_id] = context_wrap("12345")
    broker[Specs.redhat_release] = context_wrap("Red Hat Enterprise Linux Server release 7.4 (Maipo)")
    e = InsightsEvaluator(broker)
    e.process(components)
    result = e.get_response()
    assert result["system"]["hostname"] == "www.example.com"
    assert result["system"]["system_id"] == "12345"
    assert result["system"]["metadata"]["release"] == "Red Hat Enterprise Linux Server release 7.4 (Maipo)"


def test_insights_evaluator_attrs_incremental():
    broker = dr.Broker()
    broker[Specs.hostname] = context_wrap("www.example.com")
    broker[Specs.machine_id] = context_wrap("12345")
    broker[Specs.redhat_release] = context_wrap("Red Hat Enterprise Linux Server release 7.4 (Maipo)")
    with InsightsEvaluator(broker) as e:
        list(dr.run_incremental(components, broker=broker))
        result = e.get_response()
        assert result["system"]["hostname"] == "www.example.com"
        assert result["system"]["system_id"] == "12345"
        assert result["system"]["metadata"]["release"] == "Red Hat Enterprise Linux Server release 7.4 (Maipo)"


def test_insights_evaluator_attrs_incremental_process():
    broker = dr.Broker()
    broker[Specs.hostname] = context_wrap("www.example.com")
    broker[Specs.machine_id] = context_wrap("12345")
    broker[Specs.redhat_release] = context_wrap("Red Hat Enterprise Linux Server release 7.4 (Maipo)")
    e = InsightsEvaluator(broker)
    e.process(components)
    result = e.get_response()
    assert result["system"]["hostname"] == "www.example.com"
    assert result["system"]["system_id"] == "12345"
    assert result["system"]["metadata"]["release"] == "Red Hat Enterprise Linux Server release 7.4 (Maipo)"


def test_insights_evaluator_make_fail():
    broker = dr.Broker()
    broker[Specs.hostname] = context_wrap("www.example.com")
    broker[Specs.machine_id] = context_wrap("12345")
    broker[Specs.redhat_release] = context_wrap("Red Hat Enterprise Linux Server release 7.4 (Maipo)")
    e = InsightsEvaluator(broker)
    e.process(components)
    result = e.get_response()
    assert result["system"]["hostname"] == "www.example.com"
    assert result["system"]["system_id"] == "12345"
    assert result["system"]["metadata"]["release"] == "Red Hat Enterprise Linux Server release 7.4 (Maipo)"
    assert len(result["reports"]) == 2
    assert len([r["component"] for r in result["reports"]]) == 2
    assert len([r["type"] for r in result["reports"]]) == 2
    assert len([r["key"] for r in result["reports"]]) == 2


def test_insights_evaluator_make_pass():
    broker = dr.Broker()
    broker[Specs.hostname] = context_wrap("www.example.com")
    broker[Specs.machine_id] = context_wrap("12345")
    broker[Specs.redhat_release] = context_wrap("Red Hat Enterprise Linux Server release 7.4 (Maipo)")
    e = InsightsEvaluator(broker)
    e.process(components)
    result = e.get_response()
    assert result["system"]["hostname"] == "www.example.com"
    assert result["system"]["system_id"] == "12345"
    assert result["system"]["metadata"]["release"] == "Red Hat Enterprise Linux Server release 7.4 (Maipo)"
    assert len(result["pass"]) == 1
    assert len([r["component"] for r in result["pass"]]) == 1
    assert len([r["type"] for r in result["pass"]]) == 1
    assert len([r["key"] for r in result["pass"]]) == 1


def test_insights_evaluator_make_fingerprint():
    broker = dr.Broker()
    broker[Specs.hostname] = context_wrap("www.example.com")
    broker[Specs.machine_id] = context_wrap("12345")
    broker[Specs.redhat_release] = context_wrap("Red Hat Enterprise Linux Server release 7.4 (Maipo)")
    e = InsightsEvaluator(broker)
    e.process(components)
    result = e.get_response()
    assert result["system"]["hostname"] == "www.example.com"
    assert result["system"]["system_id"] == "12345"
    assert result["system"]["metadata"]["release"] == "Red Hat Enterprise Linux Server release 7.4 (Maipo)"
    assert len(result["fingerprints"]) == 1
    assert len([r["component"] for r in result["fingerprints"]]) == 1
    assert len([r["type"] for r in result["fingerprints"]]) == 1
    assert len([r["key"] for r in result["fingerprints"]]) == 1


def test_insights_evaluator_make_unsure():
    broker = dr.Broker()
    broker[Specs.hostname] = context_wrap("www.example.com")
    broker[Specs.machine_id] = context_wrap("12345")
    broker[Specs.redhat_release] = context_wrap("Red Hat Enterprise Linux Server release 7.4 (Maipo)")
    e = InsightsEvaluator(broker)
    e.process(components)
    result = e.get_response()
    assert result["system"]["hostname"] == "www.example.com"
    assert result["system"]["system_id"] == "12345"
    assert result["system"]["metadata"]["release"] == "Red Hat Enterprise Linux Server release 7.4 (Maipo)"
    assert len(result["unsure"]) == 1
    assert len([r["component"] for r in result["unsure"]]) == 1
    assert len([r["type"] for r in result["unsure"]]) == 1
    assert len([r["key"] for r in result["unsure"]]) == 1
