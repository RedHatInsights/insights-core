import time

from insights.core.dr import run
from insights.core.plugins import TimeoutException, datasource, make_info, rule
from insights.core.spec_factory import DatasourceProvider, RegistryPoint, SpecSet, foreach_execute


class Specs(SpecSet):
    spec_ds_timeout_1 = RegistryPoint()
    spec_ds_timeout_2 = RegistryPoint()
    spec_ds_timeout_default = RegistryPoint()
    spec_foreach_ds_timeout_1 = RegistryPoint(multi_output=True)


@datasource(timeout=1)
def foreach_ds_timeout_1(broker):
    time.sleep(2)
    return ['test1', 'test2', 'test3']


@datasource(timeout=1)
def ds_timeout_1(broker):
    time.sleep(2)
    return DatasourceProvider('foo', "test_ds_timeout_1")


@datasource(timeout=3)
def ds_timeout_2(broker):
    time.sleep(1)
    return DatasourceProvider('foo', "test_ds_timeout_2")


@datasource()
def ds_timeout_default(broker):
    time.sleep(1)
    return DatasourceProvider('foo', "test_ds_timeout_def")


class TestSpecs(Specs):
    spec_ds_timeout_1 = ds_timeout_1
    spec_ds_timeout_2 = ds_timeout_2
    spec_ds_timeout_default = ds_timeout_default
    spec_foreach_ds_timeout_1 = foreach_execute(foreach_ds_timeout_1, "/usr/bin/echo %s")


@rule(Specs.spec_ds_timeout_2, Specs.spec_ds_timeout_default)
def timeout_datasource_no_timeout(ds_to_2, ds_to_def):
    return make_info('INFO_1')


@rule(Specs.spec_ds_timeout_1)
def timeout_datasource_hit(ds_to_1):
    return make_info('INFO_2')


@rule(Specs.spec_foreach_ds_timeout_1)
def timeout_foreach_datasource_hit(foreach_ds_to_1):
    return make_info('INFO_2')


def test_timeout_datasource_no_hit():
    broker = run(timeout_datasource_no_timeout)
    assert timeout_datasource_no_timeout in broker
    assert "insights.tests.datasources.test_datasource_timeout.Specs.ds_timeout_2" not in broker.exceptions


def test_timeout_datasource_hit_def():
    broker = run(timeout_datasource_hit)
    assert timeout_datasource_hit in broker
    assert "insights.tests.datasources.test_datasource_timeout.Specs.spec_ds_timeout_1" in broker.exceptions
    exs = broker.exceptions["insights.tests.datasources.test_datasource_timeout.Specs.spec_ds_timeout_1"]
    assert [ex for ex in exs if isinstance(ex, TimeoutException) and str(ex) == "Datasource spec insights.tests.datasources.test_datasource_timeout.TestSpecs.spec_ds_timeout_1 timed out after 1 seconds!"]


def test_timeout_foreach_datasource_hit_def():
    broker = run(timeout_foreach_datasource_hit)
    assert timeout_foreach_datasource_hit in broker
    assert "insights.tests.datasources.test_datasource_timeout.Specs.spec_foreach_ds_timeout_1" in broker.exceptions
    exs = broker.exceptions["insights.tests.datasources.test_datasource_timeout.Specs.spec_foreach_ds_timeout_1"]
    assert [ex for ex in exs if isinstance(ex, TimeoutException) and str(ex) == "Datasource spec insights.tests.datasources.test_datasource_timeout.foreach_ds_timeout_1 timed out after 1 seconds!"]
