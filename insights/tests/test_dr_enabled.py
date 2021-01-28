from insights import combiner, dr
from insights.core.context import HostContext
from insights.parsers.uname import Uname


def teardown_function(*args):
    for k in dr.ENABLED:
        dr.ENABLED[k] = True


@combiner()
def one():
    return 1


def test_enabled_string():
    assert dr.is_enabled("insights.core.context.HostContext")


def test_enabled_object():
    assert dr.is_enabled(Uname)


def test_set_enabled_object():
    dr.set_enabled(HostContext)
    assert dr.is_enabled(HostContext)


def test_disabled_string():
    dr.set_enabled("insights.core.context.HostContext", False)
    assert not dr.is_enabled(HostContext)


def test_disabled_object():
    dr.set_enabled(Uname, False)
    assert not dr.is_enabled(Uname)


def test_disabled_run():
    assert dr.ENABLED[one]
    broker = dr.run(dr.COMPONENTS[dr.GROUPS.single])
    assert one in broker

    dr.set_enabled(one, False)
    assert not dr.ENABLED[one]
    broker = dr.run(dr.COMPONENTS[dr.GROUPS.single])
    assert one not in broker
