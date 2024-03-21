import os
import tempfile
import yaml

from mock.mock import Mock

from insights.collect import (
        load_manifest,
        default_manifest,
        _parse_broker_exceptions)
from insights.core.dr import Broker
from insights.core.exceptions import ContentException


def test_parse_broker_exceptions_no_errors():
    exc_to_report = set([OSError])
    broker = Broker()
    errors = _parse_broker_exceptions(broker, exc_to_report)
    assert not errors


def test_parse_broker_exceptions_oserror():
    exc_to_report = set([OSError])
    broker = Broker()
    component_one = Mock()
    broker.add_exception(component_one, OSError("OS Error occurred"))
    component_two = Mock()
    broker.add_exception(component_two, OSError("OS Error occurred again"))
    errors = _parse_broker_exceptions(broker, exc_to_report)
    assert OSError in errors.keys()
    assert len(errors[OSError]) == 2
    assert all(type(ex) is OSError for ex, comp in errors[OSError])


def test_parse_broker_exceptions_oserror_contentexception():
    exc_to_report = set([OSError])
    broker = Broker()
    component_one = Mock()
    broker.add_exception(component_one, OSError("OS Error occurred"))
    component_two = Mock()
    broker.add_exception(component_two, ContentException("Bad content"))
    errors = _parse_broker_exceptions(broker, exc_to_report)
    assert OSError in errors.keys()
    assert ContentException not in errors.keys()
    assert len(errors[OSError]) == 1
    assert all(type(ex) is OSError for ex, comp in errors[OSError])


def test_load_manifest():
    # dict
    data = yaml.safe_load(default_manifest)
    ret = load_manifest(data)
    assert ret == data
    # string
    ret = load_manifest(default_manifest)
    assert ret == data
    # file
    tmpfile = tempfile.NamedTemporaryFile(prefix='tmp_', suffix='_manifest_rhin', delete=False)
    tmpfile.close()
    with open(tmpfile.name, 'w') as fd:
        fd.write(default_manifest)
    ret = load_manifest(tmpfile.name)
    assert ret == data
    os.remove(tmpfile.name)
