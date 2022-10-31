import time

from insights.core.dr import TimeoutException, run
from insights.core.plugins import datasource, rule, make_info
from insights.core.spec_factory import DatasourceProvider, RegistryPoint, SpecSet


class Specs(SpecSet):
    ds_2_timeout_1_with_customized_msg = RegistryPoint()
    ds_2_timeout_1_with_default_msg = RegistryPoint()
    ds_1_timeout_2 = RegistryPoint()


class TestSpecs(Specs):
    @datasource(timeout=1, message='Over 1 second')
    def ds_2_timeout_1_with_customized_msg(broker):
        time.sleep(2)
        return DatasourceProvider('foo', "test_ds_3")

    @datasource(timeout=1)
    def ds_2_timeout_1_with_default_msg(broker):
        time.sleep(2)
        return DatasourceProvider('foo', "test_ds_2")

    @datasource(timeout=2)
    def ds_1_timeout_2(broker):
        time.sleep(1)
        return DatasourceProvider('foo', "test_ds_1")


@rule(Specs.ds_1_timeout_2)
def timeout_datasource_no_timeout(ds_12):
    return make_info('INFO')


@rule(Specs.ds_2_timeout_1_with_default_msg)
def timeout_datasource_hit_with_def_msg(ds_21_def):
    return make_info('INFO')


@rule(Specs.ds_2_timeout_1_with_customized_msg)
def timeout_datasource_hit_with_cus_msg(ds_21_cus):
    return make_info('INFO')


def test_timeout_datasource_no_hit():
    broker = run(timeout_datasource_no_timeout)
    assert timeout_datasource_no_timeout in broker
    assert TestSpecs.ds_1_timeout_2 not in broker.exceptions


def test_timeout_datasource_hit_def():
    broker = run(timeout_datasource_hit_with_def_msg)
    assert timeout_datasource_hit_with_def_msg in broker
    assert TestSpecs.ds_2_timeout_1_with_default_msg in broker.exceptions
    exs = broker.exceptions[TestSpecs.ds_2_timeout_1_with_default_msg]
    assert [ex for ex in exs if isinstance(ex, TimeoutException) and str(ex) == "Timed Out"]


def test_timeout_datasource_hit_msg():
    broker = run(timeout_datasource_hit_with_cus_msg)
    assert timeout_datasource_hit_with_cus_msg in broker
    assert TestSpecs.ds_2_timeout_1_with_customized_msg in broker.exceptions
    exs = broker.exceptions[TestSpecs.ds_2_timeout_1_with_customized_msg]
    assert [ex for ex in exs if isinstance(ex, TimeoutException) and str(ex) == "Over 1 second"]
