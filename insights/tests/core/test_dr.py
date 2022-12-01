from insights.core import dr
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider, RegistryPoint, SpecSet


class RegistrySpecs(SpecSet):
    simple_spec = RegistryPoint()
    first_spec_with_dep = RegistryPoint()
    second_spec_with_dep = RegistryPoint()


@datasource()
def simple_spec_imp(broker):
    return DatasourceProvider("some data", "/path_1")


@datasource()
def dependency_ds(broker):
    return DatasourceProvider("dependency data", "/path_2")


@datasource(dependency_ds)
def first_spec_with_dep_imp(broker):
    return DatasourceProvider("some data", "/path_3")


@datasource(dependency_ds)
def second_spec_with_dep_imp(broker):
    return DatasourceProvider("some data", "/path_4")


class DefaultSpecs(RegistrySpecs):
    simple_spec = simple_spec_imp
    first_spec_with_dep = first_spec_with_dep_imp
    second_spec_with_dep = second_spec_with_dep_imp


def test_is_registry_point():
    assert dr.is_registry_point(RegistrySpecs.simple_spec)
    assert not dr.is_registry_point(DefaultSpecs.simple_spec)


def test_get_registry_points_simple():
    specs = dr.get_registry_points(DefaultSpecs.simple_spec)
    assert len(specs) == 1
    spec = list(specs)[0]
    assert spec == RegistrySpecs.simple_spec


def test_get_registry_points_multiple_specs():
    specs = dr.get_registry_points(dependency_ds)
    assert len(specs) == 2
    for spec in specs:
        assert spec in [RegistrySpecs.first_spec_with_dep, RegistrySpecs.second_spec_with_dep]
