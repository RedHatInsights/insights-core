
from insights.core import dr
from insights.core.plugins import combiner

VALUE = "test"


@combiner(alias="my_rule")
def my_rule(broker):
    return VALUE


def test_alias():
    graph = dr.get_dependency_graph(my_rule)
    broker = dr.run(graph)
    assert broker[my_rule] == VALUE
    assert broker["my_rule"] == VALUE
