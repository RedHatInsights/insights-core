import pytest
import json
from mock.mock import patch

from insights.core import filters
from insights.core.exceptions import SkipComponent
from insights.specs import Specs
from insights.tests import context_wrap
from insights.specs.datasources.machine_ids import dup_machine_id
from insights.core.spec_factory import DatasourceProvider


class MockInsightsConfig(object):
    def __init__(self):
        self.legacy_upload = False

    def _load_config_file(self):
        pass

    def _load_env(self):
        pass


class MockInsightsConnection(object):
    def __init__(self, config):
        self.config = config
        self.base_url = ''
        self.inventory_url = ''

    def get(self, url):
        if url.endswith('45678'):
            content = json.dumps(
                {
                    'total': 1
                }
            )
        else:
            content = json.dumps(
                {
                    'total': 2
                }
            )
        return Result(content)


class Result(object):
    def __init__(self, content):
        self.content = content


def setup_function(func):
    if Specs.duplicate_machine_id in filters._CACHE:
        del filters._CACHE[Specs.duplicate_machine_id]
    if Specs.duplicate_machine_id in filters.FILTERS:
        del filters.FILTERS[Specs.duplicate_machine_id]

    if func in [test_duplicate, test_non_duplicate, test_no_spec_found, test_wrong_machine_id_content, test_machine_id_not_in_filters]:
        filters.add_filter(Specs.duplicate_machine_id, ["dc194312-8cdd-4e75-8cf1-2094bfsfsdeff"])
        filters.add_filter(Specs.duplicate_machine_id, ["dc194312-8cdd-4e75-8cf1-2094bf45678"])
    if func is test_module_filters_empty:
        filters.add_filter(Specs.duplicate_machine_id, [])


def mock_try_autoconfig(config):
    return


@patch('insights.specs.datasources.machine_ids.InsightsConnection', MockInsightsConnection)
@patch('insights.specs.datasources.machine_ids.try_auto_configuration', mock_try_autoconfig)
@patch('insights.specs.datasources.machine_ids.InsightsConfig', MockInsightsConfig)
def test_duplicate():
    broker = {Specs.machine_id: context_wrap(lines=['dc194312-8cdd-4e75-8cf1-2094bfsfsdeff'])}
    result = dup_machine_id(broker)
    expected = DatasourceProvider(content=['dc194312-8cdd-4e75-8cf1-2094bfsfsdeff'], relative_path='insights_commands/duplicate_machine_id')
    assert expected.content == result.content
    assert expected.relative_path == result.relative_path


@patch('insights.specs.datasources.machine_ids.InsightsConnection', MockInsightsConnection)
@patch('insights.specs.datasources.machine_ids.try_auto_configuration', mock_try_autoconfig)
@patch('insights.specs.datasources.machine_ids.InsightsConfig', MockInsightsConfig)
def test_non_duplicate():
    broker = {Specs.machine_id: context_wrap(lines=['dc194312-8cdd-4e75-8cf1-2094bf45678'])}
    with pytest.raises(SkipComponent):
        dup_machine_id(broker)


@patch('insights.specs.datasources.machine_ids.InsightsConnection', MockInsightsConnection)
@patch('insights.specs.datasources.machine_ids.try_auto_configuration', mock_try_autoconfig)
@patch('insights.specs.datasources.machine_ids.InsightsConfig', MockInsightsConfig)
def test_module_filters_empty():
    broker = {Specs.machine_id: context_wrap(lines=['dc194312-8cdd-4e75-8cf1-2094bfsfsdeff'])}
    with pytest.raises(SkipComponent):
        dup_machine_id(broker)


@patch('insights.specs.datasources.machine_ids.InsightsConnection', MockInsightsConnection)
@patch('insights.specs.datasources.machine_ids.try_auto_configuration', mock_try_autoconfig)
@patch('insights.specs.datasources.machine_ids.InsightsConfig', MockInsightsConfig)
def test_no_spec_found():
    with pytest.raises(SkipComponent):
        dup_machine_id({})


@patch('insights.specs.datasources.machine_ids.InsightsConnection', MockInsightsConnection)
@patch('insights.specs.datasources.machine_ids.try_auto_configuration', mock_try_autoconfig)
@patch('insights.specs.datasources.machine_ids.InsightsConfig', MockInsightsConfig)
def test_wrong_machine_id_content():
    broker = {Specs.machine_id: context_wrap(lines=['dc194312-8cdd-4e75-8cf1-2094bfsfsdeff', 'dc194312-8cdd-4e75-8cf1-2094bfsf45678'])}
    with pytest.raises(SkipComponent):
        dup_machine_id(broker)


@patch('insights.specs.datasources.machine_ids.InsightsConnection', MockInsightsConnection)
@patch('insights.specs.datasources.machine_ids.try_auto_configuration', mock_try_autoconfig)
@patch('insights.specs.datasources.machine_ids.InsightsConfig', MockInsightsConfig)
def test_machine_id_not_in_filters():
    broker = {Specs.machine_id: context_wrap(lines=['dc194312-8cdd-4e75-8cf1-2094bfsfsabc'])}
    with pytest.raises(SkipComponent):
        dup_machine_id(broker)
