import pytest

from insights.plugins.ps_rule_fakes import (psaux_no_filter,
                                            psauxww_ds_filter,
                                            psalxwww_parser_filter)
from insights.plugins.rule_with_combiner_and_parser_parser_filtered import parser_is_filtered
from insights.plugins.rule_with_combiner_and_parser_parser_not_filtered import parser_is_not_filtered
from insights.plugins.rule_with_combiner_only import parser_is_not_used
from insights.specs import Specs
from insights.tests import InputData, run_test


def test_run_test_missing_filters_exception():
    """
    The rule underlying datasource requires a filter,
    an exception should be raised because filter was not
    added in the rule module.
    """
    input_data = InputData("fake_input")
    input_data.add(Specs.ps_aux, "FAKE_CONTENT")
    with pytest.raises(Exception):
        run_test(psaux_no_filter, input_data, None)


def test_run_test_no_missing_filters_using_datasource():
    """
    Required filter was added directly to the datasouce,
    ``run_test`` should complete without any exceptions.
    """
    input_data = InputData("fake_input")
    input_data.add(Specs.ps_auxww, "FAKE_CONTENT")
    result = run_test(psauxww_ds_filter, input_data, None)
    assert result


def test_run_test_no_missing_filters_using_parser():
    """
    Required filter was added to using the parser,
    ``run_test`` should complete without any exceptions.
    """
    input_data = InputData("fake_input")
    input_data.add(Specs.ps_alxwww, "FAKE_CONTENT")
    result = run_test(psalxwww_parser_filter, input_data, None)
    assert result


def test_run_test_parser_is_not_used():
    """
    1. The rule uses one Combiner that depends upon a filterable Parser.
    2. The rule does NOT depend upon (import) the filterable Parser directly.
    3. The filterable Parser is NOT filter in the rule as well.
    """
    input_data = InputData("fake_input")
    input_data.add(Specs.dmesg, "FAKE_CONTENT")
    result = run_test(parser_is_not_used, input_data, None)
    # No Exception raised
    assert result


def test_run_test_parser_is_filtered():
    """
    1. The rule uses one Combiner that depends upon a filterable Parser.
    2. The rule does also depend upon (import) the filterable Parser directly.
    3. The filterable Parser is FILTERED in the rule.
    """
    input_data = InputData("fake_input")
    input_data.add(Specs.dmesg, "FAKE_CONTENT")
    result = run_test(parser_is_filtered, input_data, None)
    # No Exception raised
    assert result


def test_run_test_parser_is_not_filtered():
    """
    1. The rule uses one Combiner that depends upon a filterable Parser.
    2. The rule does also depend upon (import) the filterable Parser.
    3. The filterable Parser is NOT filtered in the rule.
    """
    input_data = InputData("fake_input")
    input_data.add(Specs.dmesg, "FAKE_CONTENT")
    with pytest.raises(Exception) as ex:
        run_test(parser_is_not_filtered, input_data, None)
    assert 'must add filters to' in str(ex)
