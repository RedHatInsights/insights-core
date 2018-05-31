from insights import combiner
from insights.tests import archive_provider, InputData


@combiner()
def one():
    return 1


@combiner()
def two():
    return 2


@combiner(one, two)
def three(x, y):
    return x + y


@archive_provider(three)
def integration_tests():
    data = InputData()
    data.add_component(two, 5)
    yield data, 6
