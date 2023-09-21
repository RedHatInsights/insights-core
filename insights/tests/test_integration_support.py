import pytest

from insights.plugins.ps_rule_fakes import (psaux_no_filter,
                                            psauxww_ds_filter,
                                            psalxwww_parser_filter)
from insights.plugins.combiner_rule_wo_filterable_parser import combiner_wo_filterable_parser
from insights.plugins.combiner_rule_with_filterable_parser_filtered import combiner_with_filtered_filterable_parser
from insights.plugins.combiner_rule_with_filterable_parser_not_filtered import combiner_with_filterable_parser_but_no_add_filter
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


def test_run_test_combiner_wo_filterable_parser():
    """
    1. The rule imports one Combiner that contains a filterable Parser.
    2. The rule does not import the filterable Parser.
    """
    input_data = InputData("fake_input")
    input_data.add(Specs.dmesg, "FAKE_CONTENT")
    result = run_test(combiner_wo_filterable_parser, input_data, None)
    # No Exception raised
    assert result


def test_run_test_combiner_with_filtered_filterable_parser():
    """
    1. The rule imports one Combiner that contains a filterable Parser.
    2. The rule does also import the filterable Parser.
    3. The spec of the filterable Parser is filtered in the rule.
    """
    input_data = InputData("fake_input")
    input_data.add(Specs.dmesg, "FAKE_CONTENT")
    result = run_test(combiner_with_filtered_filterable_parser, input_data, None)
    # No Exception raised
    assert result


def test_run_test_combiner_with_no_filtered_filterable_parser():
    """
    1. The rule imports one Combiner that contains a filterable Parser.
    2. The rule does also import the filterable Parser.
    3. The spec of the filterable Parser is NOT filtered in the rule.
    """
    input_data = InputData("fake_input")
    input_data.add(Specs.dmesg, "FAKE_CONTENT")
    with pytest.raises(Exception) as ex:
        run_test(combiner_with_filterable_parser_but_no_add_filter, input_data, None)
    assert 'must add filters to' in str(ex)
