from insights.plugins.ps_rule_fakes import psaux_no_filter, psauxww_ds_filter, psalxwww_parser_filter
from insights.specs import Specs
from . import InputData, run_test

import pytest


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
