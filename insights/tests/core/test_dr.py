from insights.combiners.ps import Ps
from insights.core import dr
from insights.core.plugins import datasource, condition, parser
from insights.core.spec_factory import DatasourceProvider, RegistryPoint, SpecSet
from insights.parsers.ps import PsAux
from insights.specs import Specs


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


class LocalDefaultSpecs(RegistrySpecs):
    simple_spec = simple_spec_imp
    first_spec_with_dep = first_spec_with_dep_imp
    second_spec_with_dep = second_spec_with_dep_imp


@parser(RegistrySpecs.simple_spec)
def simple_spec_condition(spec):
    return True


@condition(RegistrySpecs.first_spec_with_dep, RegistrySpecs.second_spec_with_dep)
def multiple_spec_condition(spec1, spec2):
    return True


def test_is_registry_point():
    assert dr.is_registry_point(RegistrySpecs.simple_spec)
    assert not dr.is_registry_point(LocalDefaultSpecs.simple_spec)


def test_get_registry_points_simple():
    specs = dr.get_registry_points(LocalDefaultSpecs.simple_spec)
    assert len(specs) == 1
    assert list(specs)[0] == RegistrySpecs.simple_spec

    specs = dr.get_registry_points(LocalDefaultSpecs.first_spec_with_dep)
    assert len(specs) == 1
    assert list(specs)[0] == RegistrySpecs.first_spec_with_dep

    specs = dr.get_registry_points(simple_spec_condition)
    assert len(specs) == 1
    assert list(specs)[0] == RegistrySpecs.simple_spec

    specs = dr.get_registry_points(Specs.ps_aux)
    assert len(specs) == 1
    assert list(specs)[0] == Specs.ps_aux

    specs = dr.get_registry_points(PsAux)
    assert len(specs) == 1
    assert list(specs)[0] == Specs.ps_aux


def test_get_registry_points_multiple_specs():
    specs = dr.get_registry_points(multiple_spec_condition)
    assert len(specs) == 2
    for spec in [RegistrySpecs.first_spec_with_dep, RegistrySpecs.second_spec_with_dep]:
        assert spec in specs

    specs = dr.get_registry_points(Ps)
    assert len(specs) == 6
    for spec in [Specs.ps_aux, Specs.ps_auxww, Specs.ps_auxcww, Specs.ps_ef,
                 Specs.ps_auxcww, Specs.ps_eo_cmd]:
        assert spec in specs
