from insights import dr, parser
from insights.core.plugins import component


@component()
def data():
    return [1, 2, 3, 4, 5]


@parser(data)
class Lax(object):
    count = 0

    def __init__(self, d):
        if Lax.count > 3:
            raise Exception("Lax")
        Lax.count += 1


@parser(data, continue_on_error=False)
class Boom(object):
    count = 0

    def __init__(self, d):
        if Boom.count > 3:
            raise Exception("Boom")
        Boom.count += 1


def test_dont_continue_on_error():
    Boom.count = 0
    broker = dr.run(Boom)
    assert Boom not in broker


def test_continue_on_error():
    Lax.count = 0
    broker = dr.run(Lax)
    assert len(broker[Lax]) == 4
