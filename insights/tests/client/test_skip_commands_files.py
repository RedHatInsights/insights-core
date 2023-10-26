from insights.client.data_collector import DataCollector
from insights.client.config import InsightsConfig
from insights.client.insights_spec import InsightsCommand
from insights.client.archive import InsightsArchive
from mock.mock import patch, call, MagicMock


@patch("insights.client.data_collector.DataCollector._parse_file_spec")
@patch("insights.client.data_collector.InsightsFile")
def test_omit_before_expanded_paths(InsightsFile, parse_file_spec):
    """
    Files are omitted based on representation of exact string matching in uploader.json
    """
    c = InsightsConfig(core_collect=False)
    spec_conf = {'files': [{"file": "/etc/pam.d/vsftpd", "pattern": [], "symbolic_name": "vsftpd"}], 'commands': {}}
    data_collector = DataCollector(c, spec_conf=spec_conf)
    rm_conf = {'files': ["/etc/pam.d/vsftpd"]}
    data_collector.run_collection(rm_conf, {}, '')
    parse_file_spec.assert_not_called()
    InsightsFile.assert_not_called()


@patch("insights.client.data_collector.DataCollector._parse_file_spec")
@patch("insights.client.data_collector.InsightsFile")
def test_omit_after_expanded_paths(InsightsFile, parse_file_spec):
    """
    Files are omitted based on the expanded paths of the uploader.json path
    """
    c = InsightsConfig(core_collect=False)
    spec_conf = {'files': [{"file": "/etc/yum.repos.d/()*.*\\.repo", "pattern": [], "symbolic_name": "yum_repos_d"}], 'commands': {}}
    data_collector = DataCollector(c, spec_conf=spec_conf)
    rm_conf = {'files': ["/etc/yum/repos.d/test.repo"]}
    data_collector.run_collection(rm_conf, {}, '')
    parse_file_spec.assert_called_once()
    InsightsFile.assert_not_called()


@patch("insights.client.data_collector.DataCollector._parse_file_spec")
@patch("insights.client.data_collector.InsightsFile")
@patch("insights.client.data_collector.InsightsCommand")
def test_omit_symbolic_name(InsightsCommand, InsightsFile, parse_file_spec):
    """
    Files/commands are omitted based on their symbolic name in uploader.json
    """
    c = InsightsConfig(core_collect=False)

    spec_conf = {'files': [{"file": "/etc/pam.d/vsftpd", "pattern": [], "symbolic_name": "vsftpd"}],
                        'commands': [{"command": "/sbin/chkconfig --list", "pattern": [], "symbolic_name": "chkconfig"}],
                        'pre_commands': []}
    data_collector = DataCollector(c, spec_conf=spec_conf)
    rm_conf = {'files': ["vsftpd"], "commands": ["chkconfig"]}
    data_collector.run_collection(rm_conf, {}, '')
    parse_file_spec.assert_not_called()
    InsightsFile.assert_not_called()
    InsightsCommand.assert_not_called()


@patch("insights.client.data_collector.InsightsCommand")
@patch("insights.client.data_collector.InsightsFile")
@patch("insights.client.data_collector.InsightsArchive")
@patch("insights.client.data_collector.Cleaner")
@patch("insights.client.data_collector.DataCollector._write_collection_stats", MagicMock())
def test_symbolic_name_bc(Cleaner, InsightsArchive, InsightsFile, InsightsCommand):
    """
    WICKED EDGE CASE: in case uploader.json is old and doesn't have symbolic names, don't crash
    """
    c = InsightsConfig()

    spec_conf = {'files': [{"file": "/etc/pam.d/vsftpd", "pattern": []}],
                        'commands': [{"command": "/sbin/chkconfig --list", "pattern": []}],
                        'pre_commands': []}
    rm_conf = {'files': ["vsftpd"], "commands": ["chkconfig"]}
    data_collector = DataCollector(c, spec_conf=spec_conf)
    data_collector.run_collection(rm_conf, {}, '')
    InsightsFile.assert_called_once()
    InsightsCommand.assert_called_once()
    Cleaner.assert_called_once()
    InsightsArchive.return_value.add_to_archive.assert_called()
    InsightsArchive.return_value.add_to_archive.assert_has_calls(
        [call(InsightsFile.return_value, Cleaner.return_value, ([], False)),
         call(InsightsCommand.return_value, Cleaner.return_value, ([], False))],
        any_order=True)


@patch("insights.client.archive.write_data_to_file")
def test_dont_archive_when_command_not_found(write_data_to_file):
    """
    If the command is not found do not archive it
    """
    arch = InsightsArchive(InsightsConfig(core_collect=False))
    arch.archive_dir = arch.create_archive_dir()
    arch.cmd_dir = arch.create_command_dir()

    cmd = MagicMock(spec=InsightsCommand)
    cmd.get_output.return_value = 'timeout: failed to run command blah: No such file or directory'
    cmd.archive_path = '/path/to/command'

    arch.add_to_archive(cmd)
    write_data_to_file.assert_not_called()

    cmd.get_output.return_value = '/usr/bin/command -a'

    arch.add_to_archive(cmd)
    write_data_to_file.assert_called_once()


@patch("insights.client.archive.write_data_to_file")
def test_dont_archive_when_missing_dep(write_data_to_file):
    """
    If missing dependencies do not archive it
    """
    arch = InsightsArchive(InsightsConfig(core_collect=False))
    arch.archive_dir = arch.create_archive_dir()
    arch.cmd_dir = arch.create_command_dir()

    cmd = MagicMock(spec=InsightsCommand)
    cmd.get_output.return_value = "Missing Dependencies:"
    cmd.archive_path = '/path/to/command'

    arch.add_to_archive(cmd)
    write_data_to_file.assert_not_called()


@patch("insights.client.data_collector.DataCollector._run_pre_command", return_value=['eth0'])
@patch("insights.client.data_collector.InsightsCommand")
def test_omit_after_parse_command(InsightsCommand, run_pre_command):
    """
    Files are omitted based on the expanded paths of the uploader.json path
    """
    c = InsightsConfig(core_collect=False)
    spec_conf = {'commands': [{"command": "/sbin/ethtool -i", "pattern": [], "pre_command": "iface", "symbolic_name": "ethtool"}], 'files': [], "pre_commands": {"iface": "/sbin/ip -o link | awk -F ': ' '/.*link\\/ether/ {print $2}'"}}
    data_collector = DataCollector(c, spec_conf=spec_conf)
    rm_conf = {'commands': ["/sbin/ethtool -i eth0"]}
    data_collector.run_collection(rm_conf, {}, '')
    InsightsCommand.assert_not_called()


@patch("insights.client.data_collector.DataCollector._parse_glob_spec", return_value=[{'glob': '/etc/yum.repos.d/*.repo', 'symbolic_name': 'yum_repos_d', 'pattern': [], 'file': '/etc/yum.repos.d/test.repo'}])
@patch("insights.client.data_collector.logger.warn")
def test_run_collection_logs_skipped_globs(warn, parse_glob_spec):
    c = InsightsConfig(core_collect=False)
    spec_conf = {'commands': [], 'files': [], 'globs': [{'glob': '/etc/yum.repos.d/*.repo', 'symbolic_name': 'yum_repos_d', 'pattern': []}]}
    data_collector = DataCollector(c, spec_conf=spec_conf)
    rm_conf = {'files': ["/etc/yum.repos.d/test.repo"]}
    data_collector.run_collection(rm_conf, {}, '')
    warn.assert_called_once_with("WARNING: Skipping file %s", "/etc/yum.repos.d/test.repo")


@patch("insights.client.data_collector.logger.warn")
def test_run_collection_logs_skipped_files_by_file(warn):
    c = InsightsConfig(core_collect=False)
    spec_conf = {'commands': [], 'files': [{'file': '/etc/machine-id', 'pattern': [], 'symbolic_name': 'etc_machine_id'}], 'globs': []}
    data_collector = DataCollector(c, spec_conf=spec_conf)
    rm_conf = {'files': ["/etc/machine-id"]}
    data_collector.run_collection(rm_conf, {}, '')
    warn.assert_called_once_with("WARNING: Skipping file %s", "/etc/machine-id")


@patch("insights.client.data_collector.logger.warn")
def test_run_collection_logs_skipped_files_by_symbolic_name(warn):
    c = InsightsConfig(core_collect=False)
    spec_conf = {'commands': [], 'files': [{'file': '/etc/machine-id', 'pattern': [], 'symbolic_name': 'etc_machine_id'}], 'globs': []}
    data_collector = DataCollector(c, spec_conf=spec_conf)
    rm_conf = {'files': ["etc_machine_id"]}
    data_collector.run_collection(rm_conf, {}, '')
    warn.assert_called_once_with("WARNING: Skipping file %s", "/etc/machine-id")


@patch("insights.client.data_collector.DataCollector._parse_file_spec", return_value=[{'file': '/etc/sysconfig/network-scripts/ifcfg-enp0s3', 'pattern': [], 'symbolic_name': 'ifcfg'}])
@patch("insights.client.data_collector.logger.warn")
def test_run_collection_logs_skipped_files_by_wildcard(warn, parse_file_spec):
    c = InsightsConfig(core_collect=False)
    spec_conf = {'commands': [], 'files': [{'file': '/etc/sysconfig/network-scripts/()*ifcfg-.*', 'pattern': [], 'symbolic_name': 'ifcfg'}], 'globs': []}
    data_collector = DataCollector(c, spec_conf=spec_conf)
    rm_conf = {'files': ["/etc/sysconfig/network-scripts/ifcfg-enp0s3"]}
    data_collector.run_collection(rm_conf, {}, '')
    warn.assert_called_once_with("WARNING: Skipping file %s", "/etc/sysconfig/network-scripts/ifcfg-enp0s3")


@patch("insights.client.data_collector.logger.warn")
def test_run_collection_logs_skipped_commands_by_command(warn):
    c = InsightsConfig(core_collect=False)
    spec_conf = {'commands': [{'command': '/bin/date', 'pattern': [], 'symbolic_name': 'date'}], 'files': [], 'globs': []}
    data_collector = DataCollector(c, spec_conf=spec_conf)
    rm_conf = {'commands': ["/bin/date"]}
    data_collector.run_collection(rm_conf, {}, '')
    warn.assert_called_once_with("WARNING: Skipping command %s", "/bin/date")


@patch("insights.client.data_collector.logger.warn")
def test_run_collection_logs_skipped_commands_by_symbolic_name(warn):
    c = InsightsConfig(core_collect=False)
    spec_conf = {'commands': [{'command': '/bin/date', 'pattern': [], 'symbolic_name': 'date'}], 'files': [], 'globs': []}
    data_collector = DataCollector(c, spec_conf=spec_conf)
    rm_conf = {'commands': ["date"]}
    data_collector.run_collection(rm_conf, {}, '')
    warn.assert_called_once_with("WARNING: Skipping command %s", "/bin/date")


@patch("insights.client.data_collector.DataCollector._parse_command_spec", return_value=[{'command': '/sbin/ethtool enp0s3', 'pattern': [], 'pre_command': 'iface', 'symbolic_name': 'ethtool'}])
@patch("insights.client.data_collector.logger.warn")
def test_run_collection_logs_skipped_commands_by_pre_command(warn, parse_command_spec):
    c = InsightsConfig(core_collect=False)
    spec_conf = {'commands': [{'command': '/sbin/ethtool', 'pattern': [], 'pre_command': 'iface', 'symbolic_name': 'ethtool'}], 'files': [], 'globs': [], 'pre_commands': {'iface': '/sbin/ip -o link | awk -F \': \' \'/.*link\\/ether/ {print $2}\''}}
    data_collector = DataCollector(c, spec_conf=spec_conf)
    rm_conf = {'commands': ["/sbin/ethtool enp0s3"]}
    data_collector.run_collection(rm_conf, {}, '')
    warn.assert_called_once_with("WARNING: Skipping command %s", "/sbin/ethtool enp0s3")
