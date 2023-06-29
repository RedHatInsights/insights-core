import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import iris
from insights.tests import context_wrap


IRIS_RUNNING = """

Configuration 'IRIS'   (default)
    directory:    /intersystems
    versionid:    2023.1.0.235.1com
    datadir:      /intersystems
    conf file:    iris.cpf  (SuperServer port = 1972, WebServer = 52773)
    status:       running, since Tue Jun 27 01:55:25 2023
    state:        ok
    product:      InterSystems IRIS
""".strip()

IRIS_DOWN = """

Configuration 'IRIS'   (default)
    directory:    /intersystems
    versionid:    2023.1.0.235.1com
    datadir:      /intersystems
    conf file:    iris.cpf  (SuperServer port = 1972, WebServer = 52773)
    status:       down, last used Tue Jun 27 01:50:36 2023
    product:      InterSystems IRIS
""".strip()

IRIS_NO_CONTENT = """"""


def test_iris_list():
    iris_running = iris.IrisList(context_wrap(IRIS_RUNNING))
    assert iris_running['name'] == "IRIS"
    assert iris_running['status'] == "running, since Tue Jun 27 01:55:25 2023"
    assert 'state' in iris_running
    assert iris_running.is_running

    iris_down = iris.IrisList(context_wrap(IRIS_DOWN))
    assert iris_down['name'] == "IRIS"
    assert iris_down['status'] == "down, last used Tue Jun 27 01:50:36 2023"
    assert 'state' not in iris_down
    assert not iris_down.is_running


def test_fail():
    with pytest.raises(SkipComponent) as e:
        iris.IrisList(context_wrap(IRIS_NO_CONTENT))
    assert "The result is empty" in str(e)


def test_doc_examples():
    env = {
        'iris_info': iris.IrisList(
            context_wrap(IRIS_RUNNING)),
    }
    failed, total = doctest.testmod(iris, globs=env)
    assert failed == 0
