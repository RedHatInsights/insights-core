from insights import combiner, dr


@combiner()
def one():
    return 1


@combiner()
def two():
    return 2


@combiner(one, two)
def add(a, b):
    return a + b


def test_order_cache():
    group = dr.COMPONENTS[dr.GROUPS.single]
    gid = id(group)
    assert gid not in dr.ORDER_CACHE
    dr.run(group)
    assert gid in dr.ORDER_CACHE
