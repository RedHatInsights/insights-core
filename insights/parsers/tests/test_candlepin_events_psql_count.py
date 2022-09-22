import pytest
from insights.parsers import ParseException, SkipException
from insights.parsers.candlepin_events_psql_count import CandlepinEventsPsqlCount
from insights.tests import context_wrap


EXPECTED = 8037
EXAMPLE_OK = """
 count 
-------
  8037
(1 row)

"""   # noqa: W291
EXAMPLE_STRANGE = """
 count 
-------
  hello
(1 row)

"""   # noqa: W291
EXAMPLE_EMPTY = ""


def test_candlepin_events_psql_count():
    candlepin_events_psql_count = CandlepinEventsPsqlCount(context_wrap(EXAMPLE_OK))
    assert candlepin_events_psql_count is not None
    assert candlepin_events_psql_count.count == EXPECTED
    with pytest.raises(ParseException):
        candlepin_events_psql_count = CandlepinEventsPsqlCount(context_wrap(EXAMPLE_STRANGE))
    with pytest.raises(SkipException):
        candlepin_events_psql_count = CandlepinEventsPsqlCount(context_wrap(EXAMPLE_EMPTY))
