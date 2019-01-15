from insights.client.data_collector import DataCollector
from insights.client.config import InsightsConfig
from mock.mock import patch


@patch("insights.client.data_collector.DataCollector._parse_file_spec")
@patch("insights.client.data_collector.InsightsFile")
def test_omit_before_expanded_paths(InsightsFile, parse_file_spec):
    """
    Configuration from a file is passed to the DataCollector along with removed files configuration.
    """
    c = InsightsConfig()
    data_collector = DataCollector(c)

    collection_rules = {'files': [{"file": "/etc/pam.d/vsftpd", "pattern": [], "symbolic_name": "vsftpd"}], 'commands': {}}
    rm_conf = {'files': ["/etc/pam.d/vsftpd"]}
    data_collector.run_collection(collection_rules, rm_conf, {})
    parse_file_spec.assert_not_called()
    InsightsFile.assert_not_called()


@patch("insights.client.data_collector.DataCollector._parse_file_spec")
@patch("insights.client.data_collector.InsightsFile")
def test_omit_after_expanded_paths(InsightsFile, parse_file_spec):
    """
    Configuration from a file is passed to the DataCollector along with removed files configuration.
    """
    c = InsightsConfig()
    data_collector = DataCollector(c)

    collection_rules = {'files': [{"file": "/etc/yum.repos.d/()*.*\\.repo", "pattern": [], "symbolic_name": "yum_repos_d"}], 'commands': {}}
    rm_conf = {'files': ["/etc/yum/repos.d/test.repo"]}
    data_collector.run_collection(collection_rules, rm_conf, {})
    parse_file_spec.assert_called_once()
    InsightsFile.assert_not_called()
