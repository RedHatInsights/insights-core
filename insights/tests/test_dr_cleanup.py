from insights.core import dr


stage = dr.new_component_type()


class Base(object):
    def __init__(self, broker):
        self.clean = False

    def cleanup(self):
        self.clean = True


@stage()
class A(Base):
    pass


@stage(requires=[A])
class B(Base):
    pass


@stage(requires=[A])
class C(Base):
    pass


@stage(requires=[B, C])
class D(Base):
    def __init__(self, broker):
        super(D, self).__init__(broker)
        assert broker[A].clean
        assert not broker[B].clean
        assert not broker[C].clean


@stage(requires=[D])
class E(Base):
    def __init__(self, broker):
        super(E, self).__init__(broker)
        assert broker[B].clean
        assert broker[C].clean
        assert not broker[D].clean


def test_cleanup():
    broker = dr.Broker(cleanup=True)
    graph = dr.get_dependency_graph(E)
    broker = dr.run(graph, broker=broker)
    assert broker[A].clean
    assert broker[B].clean
    assert broker[C].clean
    assert broker[D].clean
    assert broker[E].clean
