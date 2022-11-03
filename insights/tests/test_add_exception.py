import os
import json
from tempfile import mkdtemp
from insights.core import dr
from insights.core.plugins import datasource, rule, make_info, ContentException
from insights.core.spec_factory import RegistryPoint, SpecSet
from insights.core.serde import Hydration
from insights.util import fs


class Specs(SpecSet):
    the_data = RegistryPoint()


class TestSpecs(Specs):
    @datasource()
    def the_data(broker):
        raise ContentException('Fake Datasource')


@rule(Specs.the_data)
def report(dt):
    return make_info('INFO_1')


def test_add_exception_tracebacks():
    broker = dr.run(report)
    assert report in broker
    assert TestSpecs.the_data in broker.exceptions
    all_exs = broker.exceptions[TestSpecs.the_data]
    exs = [ex for ex in all_exs if isinstance(ex, ContentException) and str(ex) == "Fake Datasource"]
    assert len(exs) == 1
    tb = broker.tracebacks[exs[0]]
    assert type(tb) is str
    assert "Traceback" in tb
    assert "Fake Datasource" in tb


def test_add_exception_tracebacks_in_meta_data_file():
    broker = dr.run(report)
    tmp_path = mkdtemp()
    spec_the_data = TestSpecs.the_data
    try:
        h = Hydration(tmp_path)
        h.dehydrate(spec_the_data, broker)
        fn = ".".join([dr.get_name(spec_the_data), h.ser_name])
        meta_data_json = os.path.join(h.meta_data, fn)
        assert os.path.exists(meta_data_json)
        with open(meta_data_json, 'r') as fp:
            ret = json.load(fp)
            exc = next(iter(broker.tracebacks))
            tb = broker.tracebacks[exc]
            assert "errors" in ret
            assert ret["errors"][0] == tb
            assert "Traceback" in tb
            assert "Fake Datasource" in tb
    finally:
        fs.remove(tmp_path)
