from insights.client.data_collector import DataCollector
from insights.client.config import InsightsConfig
from mock.mock import patch, call


@patch("insights.client.data_collector.DataCollector._parse_file_spec")
@patch("insights.client.data_collector.InsightsFile")
def test_omit_before_expanded_paths(InsightsFile, parse_file_spec):
    """
    Files are omitted based on representation of exact string matching in uploader.json
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
    Files are omitted based on the expanded paths of the uploader.json path
    """
    c = InsightsConfig()
    data_collector = DataCollector(c)

    collection_rules = {'files': [{"file": "/etc/yum.repos.d/()*.*\\.repo", "pattern": [], "symbolic_name": "yum_repos_d"}], 'commands': {}}
    rm_conf = {'files': ["/etc/yum/repos.d/test.repo"]}
    data_collector.run_collection(collection_rules, rm_conf, {})
    parse_file_spec.assert_called_once()
    InsightsFile.assert_not_called()


@patch("insights.client.data_collector.DataCollector._parse_file_spec")
@patch("insights.client.data_collector.InsightsFile")
@patch("insights.client.data_collector.InsightsCommand")
def test_omit_symbolic_name(InsightsCommand, InsightsFile, parse_file_spec):
    """
    Files/commands are omitted based on their symbolic name in uploader.json
    """
    c = InsightsConfig()
    data_collector = DataCollector(c)

    collection_rules = {'files': [{"file": "/etc/pam.d/vsftpd", "pattern": [], "symbolic_name": "vsftpd"}],
                        'commands': [{"command": "/sbin/chkconfig --list", "pattern": [], "symbolic_name": "chkconfig"}],
                        'pre_commands': []}
    rm_conf = {'files': ["vsftpd"], "commands": ["chkconfig"]}
    data_collector.run_collection(collection_rules, rm_conf, {})
    parse_file_spec.assert_not_called()
    InsightsFile.assert_not_called()
    InsightsCommand.assert_not_called()


@patch("insights.client.data_collector.InsightsCommand")
@patch("insights.client.data_collector.InsightsFile")
@patch("insights.client.data_collector.archive.InsightsArchive")
def test_symbolic_name_bc(InsightsArchive, InsightsFile, InsightsCommand):
    """
    WICKED EDGE CASE: in case uploader.json is old and doesn't have symbolic names, don't crash
    """
    c = InsightsConfig()
    data_collector = DataCollector(c)

    collection_rules = {'files': [{"file": "/etc/pam.d/vsftpd", "pattern": []}],
                        'commands': [{"command": "/sbin/chkconfig --list", "pattern": []}],
                        'pre_commands': []}
    rm_conf = {'files': ["vsftpd"], "commands": ["chkconfig"]}
    data_collector.run_collection(collection_rules, rm_conf, {})
    InsightsFile.assert_called_once()
    InsightsCommand.assert_called_once()
    InsightsArchive.return_value.add_to_archive.assert_has_calls(
        [call(InsightsFile.return_value), call(InsightsCommand.return_value)],
        any_order=True)
