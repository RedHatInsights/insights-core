import time

from insights.core import dr
from insights.core.context import HostContext, SosArchiveContext
from insights.core.exceptions import TimeoutException
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider, RegistryPoint, SpecSet, foreach_execute


class Specs(SpecSet):
    spec_ds_timeout_1_2 = RegistryPoint()
    spec_ds_timeout_3_1 = RegistryPoint()
    spec_ds_timeout_default_1 = RegistryPoint()
    spec_foreach_ds_timeout_1_2 = RegistryPoint(multi_output=True)


@datasource(timeout=1)
def foreach_ds_timeout_1_2(broker):
    time.sleep(2)
    return ['test1', 'test2', 'test3']


@datasource(timeout=1)
def ds_timeout_1_2(broker):
    time.sleep(2)
    return DatasourceProvider('foo', "test_ds_timeout_1_2")


@datasource(timeout=3)
def ds_timeout_3_1(broker):
    time.sleep(1)
    return DatasourceProvider('foo', "test_ds_timeout_3_1_")


@datasource()
def ds_timeout_default_1(broker):
    time.sleep(1)
    return DatasourceProvider('foo', "test_ds_timeout_default_1")


class TestSpecs(Specs):
    spec_ds_timeout_1_2 = ds_timeout_1_2
    spec_ds_timeout_3_1 = ds_timeout_3_1
    spec_ds_timeout_default_1 = ds_timeout_default_1
    spec_foreach_ds_timeout_1_2 = foreach_execute(foreach_ds_timeout_1_2, "/usr/bin/echo %s")

#
# TEST
#


def test_timeout_datasource_no_hit():
    broker = dr.Broker()
    broker[HostContext] = HostContext()
    persist = set([
        TestSpecs.spec_ds_timeout_3_1,
        TestSpecs.spec_ds_timeout_default_1,
    ])

    dr.run_all(persist, broker=broker)

    assert ds_timeout_3_1 in broker
    assert ds_timeout_default_1 in broker


def test_timeout_datasource_hit():
    broker = dr.Broker()
    broker[HostContext] = HostContext()
    persist = set([
        TestSpecs.spec_ds_timeout_1_2,
        TestSpecs.spec_ds_timeout_default_1,
        TestSpecs.spec_ds_timeout_3_1,
    ])

    dr.run_all(persist, broker=broker)

    assert ds_timeout_3_1 in broker
    assert ds_timeout_default_1 in broker
    assert ds_timeout_1_2 not in broker
    assert Specs.spec_ds_timeout_1_2 in broker.exceptions
    exs = broker.exceptions[Specs.spec_ds_timeout_1_2]
    assert [ex for ex in exs if isinstance(ex, TimeoutException) and str(ex) == "Datasource spec insights.tests.datasources.test_datasource_timeout.TestSpecs.spec_ds_timeout_1_2 timed out after 1 seconds!"]


def test_timeout_foreach_datasource_hit():
    broker = dr.Broker()
    broker[HostContext] = HostContext()
    persist = set([
        TestSpecs.spec_ds_timeout_3_1,
        TestSpecs.spec_ds_timeout_default_1,
        TestSpecs.spec_foreach_ds_timeout_1_2,
    ])

    dr.run_all(persist, broker=broker)

    assert ds_timeout_3_1 in broker
    assert ds_timeout_default_1 in broker
    assert foreach_ds_timeout_1_2 not in broker
    assert Specs.spec_foreach_ds_timeout_1_2 in broker.exceptions
    exs = broker.exceptions[Specs.spec_foreach_ds_timeout_1_2]
    assert [ex for ex in exs if isinstance(ex, TimeoutException) and str(ex) == "Datasource spec insights.tests.datasources.test_datasource_timeout.foreach_ds_timeout_1_2 timed out after 1 seconds!"]


def test_not_hostcontext_timeout_datasource_hit():
    broker = dr.Broker()
    broker[SosArchiveContext] = SosArchiveContext()
    persist = set([
        TestSpecs.spec_ds_timeout_3_1,
        TestSpecs.spec_ds_timeout_default_1,
        TestSpecs.spec_ds_timeout_1_2,
    ])

    dr.run_all(persist, broker=broker)

    assert ds_timeout_3_1 in broker
    assert ds_timeout_default_1 in broker
    assert ds_timeout_1_2 in broker
    assert Specs.spec_ds_timeout_1_2 not in broker.exceptions


def test_not_hostcontext_timeout_foreach_datasource_hit():
    broker = dr.Broker()
    broker[SosArchiveContext] = SosArchiveContext()
    persist = set([
        TestSpecs.spec_ds_timeout_3_1,
        TestSpecs.spec_ds_timeout_default_1,
        TestSpecs.spec_foreach_ds_timeout_1_2
    ])

    dr.run_all(persist, broker=broker)

    assert ds_timeout_3_1 in broker
    assert ds_timeout_default_1 in broker
    assert foreach_ds_timeout_1_2 in broker
    assert Specs.spec_foreach_ds_timeout_1_2 not in broker.exceptions
