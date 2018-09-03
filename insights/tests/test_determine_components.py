from insights import dr


class needs(dr.ComponentType):
    group = "needs"


@needs()
def one():
    return 1


@needs()
def two():
    return 2


@needs(one, two)
def report(a, b):
    return a + b


def test_single_component():
    graph = dr.get_dependency_graph(report)
    components = dr._determine_components(report)
    assert graph == components


def test_list_of_components():
    graph = dr.get_dependency_graph(report)
    components = dr._determine_components([one, two, report])
    assert graph == components


def test_group():
    graph = dr.get_dependency_graph(report)
    components = dr._determine_components("needs")
    assert graph == components


def test_type():
    graph = dr.get_dependency_graph(report)
    components = dr._determine_components(needs)
    assert graph == components
