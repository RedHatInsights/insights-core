from insights.core import dr
from insights.core import Parser
from insights.core.exceptions import ParseException, ContentException
from insights.core.plugins import datasource, parser, rule, make_info
from insights.core.spec_factory import DatasourceProvider, RegistryPoint, SpecSet

from insights.tests import InputData
from insights.tests import run_input_data

EXPECTED_MSG_1 = 'Invalid Data 1'
EXPECTED_MSG_2 = 'Invalid Data 2'
EXPECTED_MSG_3 = 'Invalid Data 3'


class Specs(SpecSet):
    the_ce_data = RegistryPoint()
    the_ex_data = RegistryPoint()
    the_ds_data = RegistryPoint()


@datasource()
def SomeData(broker):
    return DatasourceProvider("invalid data", "dummy")


class TestSpecs(Specs):
    @datasource()
    def the_ce_data(broker):
        raise ContentException(EXPECTED_MSG_1)

    @datasource()
    def the_ex_data(broker):
        raise Exception(EXPECTED_MSG_2)
    the_ds_data = SomeData


@parser(Specs.the_ds_data)
class SomeParser(Parser):
    def parse_content(self, content):
        raise ParseException(EXPECTED_MSG_3)


@rule(Specs.the_ce_data, Specs.the_ex_data)
def report(dt):
    return make_info('INFO_1')

#
# TEST
#


def test_broker_spec_exceptions():
    broker = dr.run(report)
    assert report in broker
    assert Specs.the_ce_data in broker.exceptions
    spec_exs = broker.exceptions[Specs.the_ce_data]
    exs = [ex for ex in spec_exs if isinstance(ex, ContentException)]
    assert len(exs) == 1
    tb = broker.tracebacks[exs[0]]
    assert type(tb) is str
    assert "Traceback" in tb
    assert EXPECTED_MSG_1 in tb

    assert Specs.the_ex_data in broker.exceptions
    spec_exs = broker.exceptions[Specs.the_ex_data]
    exs = [ex for ex in spec_exs if isinstance(ex, Exception)]
    assert len(exs) == 1
    tb = broker.tracebacks[exs[0]]
    assert type(tb) is str
    assert "Traceback" in tb
    assert EXPECTED_MSG_2 in tb


def test_broker_parse_exception():
    broker = run_input_data(SomeParser, InputData())
    assert SomeParser in broker.exceptions
    exs = broker.exceptions[SomeParser]
    exs = [ex for ex in exs if isinstance(ex, ParseException)]
    assert len(exs) == 1
    tb = broker.tracebacks[exs[0]]
    assert type(tb) is str
    assert "Traceback" in tb
    assert EXPECTED_MSG_3 in tb
