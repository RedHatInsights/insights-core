from insights.core import dr


class stage(dr.ComponentType):
    pass


@stage("dep1")
def stage1(dep1):
    return "stage1"


@stage("dep2")
def stage2(dep2):
    return "stage2"


@stage("common")
def stage3(common):
    return common


@stage("common")
def stage4(common):
    return common


def test_run():
    broker = dr.Broker()
    broker["common"] = 3
    graph = dr.get_dependency_graph(stage3)
    graph.update(dr.get_dependency_graph(stage4))
    broker = dr.run(graph, broker)

    assert stage3 in broker.instances
    assert broker[stage3] == 3

    assert stage4 in broker.instances
    assert broker[stage4] == 3


def test_run_incremental():
    broker = dr.Broker()
    broker["dep1"] = 1
    broker["dep2"] = 2
    broker["common"] = 3

    graph = dr.get_dependency_graph(stage1)
    graph.update(dr.get_dependency_graph(stage2))
    graph.update(dr.get_dependency_graph(stage3))
    graph.update(dr.get_dependency_graph(stage4))

    brokers = list(dr.run_incremental(graph, broker))
    assert len(brokers) == 3
