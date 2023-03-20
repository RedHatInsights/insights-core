from mock.mock import Mock

from insights.collect import _parse_broker_exceptions
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
