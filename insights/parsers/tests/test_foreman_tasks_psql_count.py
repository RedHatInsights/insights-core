import pytest
from insights.parsers import ParseException, SkipException
from insights.parsers.foreman_tasks_psql_count import ForemanTasksPsqlCount
from insights.tests import context_wrap


EXPECTED = 209
EXAMPLE_OK = """
 count 
-------
   209
(1 row)

"""   # noqa: W291
EXAMPLE_STRANGE = """
 count 
-------
  hello
(1 row)

"""   # noqa: W291
EXAMPLE_EMPTY = ""


def test_foreman_tasks_psql_count():
    foreman_tasks_psql_count = ForemanTasksPsqlCount(context_wrap(EXAMPLE_OK))
    assert foreman_tasks_psql_count is not None
    assert foreman_tasks_psql_count.count == EXPECTED
    with pytest.raises(ParseException):
        foreman_tasks_psql_count = ForemanTasksPsqlCount(context_wrap(EXAMPLE_STRANGE))
    with pytest.raises(SkipException):
        foreman_tasks_psql_count = ForemanTasksPsqlCount(context_wrap(EXAMPLE_EMPTY))
