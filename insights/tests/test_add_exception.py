from insights.core import dr
from insights.core.plugins import datasource, rule, make_info, ContentException
from insights.core.spec_factory import RegistryPoint, SpecSet


class Specs(SpecSet):
    the_data = RegistryPoint()


class TestSpecs(Specs):
    @datasource()
    def the_data(broker):
        raise ContentException('Fake Datasource')


@rule(Specs.the_data)
def report(dt):
    return make_info('INFO_1')


def test_broker_add_exception():
    broker = dr.run(report)
    assert report in broker
    assert Specs.the_data in broker.exceptions
    spec_exs = broker.exceptions[Specs.the_data]
    exs = [ex for ex in spec_exs if isinstance(ex, ContentException) and str(ex) == "Fake Datasource"]
    assert len(exs) == 1
    tb = broker.tracebacks[exs[0]]
    assert type(tb) is str
    assert "Traceback" in tb
    assert "Fake Datasource" in tb
