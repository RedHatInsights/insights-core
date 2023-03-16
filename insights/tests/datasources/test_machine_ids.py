import json
from mock.mock import patch
import pytest

from insights.tests import context_wrap
from insights.core.spec_factory import DatasourceProvider
from insights.specs.datasources.machine_ids import dup_machine_id_info
from insights.core import filters
from insights.core.exceptions import SkipComponent
from insights.specs import Specs


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
                    'total': 1,
                    "count": 1,
                    "page": 1,
                    "per_page": 50,
                    "results": [
                        {
                            "insights_id": "95160ae3-1ee1-40e1-9666-316dbb9270dd",
                            "subscription_manager_id": "a5a71082-1d09-4fc8-bffc-ad326e24df6a",
                            "satellite_id": None,
                            "ip_addresses": [
                                "10.0.222.82"
                            ],
                            "fqdn": "hostname1.compute.internal",

                        }
                    ]
                }
            )
        elif url.endswith('deff'):
            content = json.dumps(
                {
                    'total': 2,
                    "count": 2,
                    "page": 1,
                    "per_page": 50,
                    "results": [
                        {
                            "insights_id": "95160ae3-1ee1-40e1-9666-316dbb927ff1",
                            "subscription_manager_id": "sfwerwfsf-1d09-4fc8-bffc-sfxcsfsf",
                            "satellite_id": None,
                            "ip_addresses": [
                                "10.0.222.82"
                            ],
                            "fqdn": "hostname1.compute.internal",

                        },
                        {
                            "insights_id": "95160ae3-1ee1-40e1-9666-316dbb927ff1",
                            "subscription_manager_id": "sfweswersf-1d09-4fc8-bffc-sfxcssdf",
                            "satellite_id": None,
                            "ip_addresses": [
                                "10.0.222.83"
                            ],
                            "fqdn": "hostname2.compute.internal",

                        }
                    ]
                }
            )
        elif url.endswith('wrong'):
            content = "wrong result"
        return Result(content)


class Result(object):
    def __init__(self, content):
        self.content = content


def setup_function(func):
    if Specs.duplicate_machine_id in filters._CACHE:
        del filters._CACHE[Specs.duplicate_machine_id]
    if Specs.duplicate_machine_id in filters.FILTERS:
        del filters.FILTERS[Specs.duplicate_machine_id]

    if func in [test_duplicate, test_non_duplicate, test_wrong_machine_id_content, test_machine_id_not_in_filters, test_api_result_not_in_json_format]:
        filters.add_filter(Specs.duplicate_machine_id, ["dc194312-8cdd-4e75-8cf1-2094bfsfsdeff"])
        filters.add_filter(Specs.duplicate_machine_id, ["dc194312-8cdd-4e75-8cf1-2094bf45678"])
        filters.add_filter(Specs.duplicate_machine_id, ["dc194312-8cdd-4e75-8cf1-2094bfwrong"])
    if func is test_module_filters_empty:
        filters.add_filter(Specs.duplicate_machine_id, [])


def mock_try_autoconfig(config):
    return


@patch('insights.specs.datasources.machine_ids.InsightsConnection', MockInsightsConnection)
@patch('insights.specs.datasources.machine_ids.try_auto_configuration', mock_try_autoconfig)
@patch('insights.specs.datasources.machine_ids.InsightsConfig', MockInsightsConfig)
def test_duplicate():
    broker = {Specs.machine_id: context_wrap(lines=['dc194312-8cdd-4e75-8cf1-2094bfsfsdeff'])}
    result = dup_machine_id_info(broker)
    expected = DatasourceProvider(content=["dc194312-8cdd-4e75-8cf1-2094bfsfsdeff hostname1.compute.internal,hostname2.compute.internal"], relative_path='insights_commands/duplicate_machine_id_info')
    assert expected.content == result.content
    assert expected.relative_path == result.relative_path


@patch('insights.specs.datasources.machine_ids.InsightsConnection', MockInsightsConnection)
@patch('insights.specs.datasources.machine_ids.try_auto_configuration', mock_try_autoconfig)
@patch('insights.specs.datasources.machine_ids.InsightsConfig', MockInsightsConfig)
def test_non_duplicate():
    broker = {Specs.machine_id: context_wrap(lines=['dc194312-8cdd-4e75-8cf1-2094bf45678'])}
    with pytest.raises(SkipComponent):
        dup_machine_id_info(broker)


@patch('insights.specs.datasources.machine_ids.InsightsConnection', MockInsightsConnection)
@patch('insights.specs.datasources.machine_ids.try_auto_configuration', mock_try_autoconfig)
@patch('insights.specs.datasources.machine_ids.InsightsConfig', MockInsightsConfig)
def test_module_filters_empty():
    broker = {Specs.machine_id: context_wrap(lines=['dc194312-8cdd-4e75-8cf1-2094bfsfsdeff'])}
    with pytest.raises(SkipComponent):
        dup_machine_id_info(broker)


@patch('insights.specs.datasources.machine_ids.InsightsConnection', MockInsightsConnection)
@patch('insights.specs.datasources.machine_ids.try_auto_configuration', mock_try_autoconfig)
@patch('insights.specs.datasources.machine_ids.InsightsConfig', MockInsightsConfig)
def test_wrong_machine_id_content():
    broker = {Specs.machine_id: context_wrap(lines=['dc194312-8cdd-4e75-8cf1-2094bfsfsdeff', 'dc194312-8cdd-4e75-8cf1-2094bfsf45678'])}
    with pytest.raises(SkipComponent):
        dup_machine_id_info(broker)


@patch('insights.specs.datasources.machine_ids.InsightsConnection', MockInsightsConnection)
@patch('insights.specs.datasources.machine_ids.try_auto_configuration', mock_try_autoconfig)
@patch('insights.specs.datasources.machine_ids.InsightsConfig', MockInsightsConfig)
def test_machine_id_not_in_filters():
    broker = {Specs.machine_id: context_wrap(lines=['dc194312-8cdd-4e75-8cf1-2094bfsfsabc'])}
    with pytest.raises(SkipComponent):
        dup_machine_id_info(broker)


@patch('insights.specs.datasources.machine_ids.InsightsConnection', MockInsightsConnection)
@patch('insights.specs.datasources.machine_ids.try_auto_configuration', mock_try_autoconfig)
@patch('insights.specs.datasources.machine_ids.InsightsConfig', MockInsightsConfig)
def test_api_result_not_in_json_format():
    broker = {Specs.machine_id: context_wrap(lines=['dc194312-8cdd-4e75-8cf1-2094bfwrong'])}
    with pytest.raises(SkipComponent):
        dup_machine_id_info(broker)
