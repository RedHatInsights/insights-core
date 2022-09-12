from collections import namedtuple
from contextlib import contextmanager
from json import dump
from os import mkdir
from os.path import join
from shutil import rmtree
from tempfile import mkdtemp

from mock.mock import call
from mock.mock import Mock
from mock.mock import patch
from pytest import mark

from insights.client.config import InsightsConfig
from insights.client.data_collector import CleanOptions
from insights.contrib.soscleaner import SOSCleaner

ReportItem = namedtuple("ReportItem", ("name", "relative_path"))


def _soscleaner():
    soscleaner = SOSCleaner()
    soscleaner.logger = Mock()
    return soscleaner


@contextmanager
def _mock_report_dir(report_items):
    tmpdir = mkdtemp()
    try:
        hostname_path = join(tmpdir, "hostname")
        with open(hostname_path, "w") as hostname_file:
            hostname_file.write("test-hostname")

        data_path = join(tmpdir, "data")
        meta_data_path = join(tmpdir, "meta_data")
        for path in [data_path, meta_data_path]:
            mkdir(path)

        for report_item in report_items:
            json_path = join(
                meta_data_path, "%s.json" % report_item.name
            )
            with open(json_path, "w") as json_file:
                meta_data_obj = {
                    "name": report_item.name,
                    "results": {
                        "object": {
                            "relative_path": report_item.relative_path
                        }
                    }
                }
                dump(meta_data_obj, json_file)

        yield tmpdir
    finally:
        rmtree(tmpdir)


@mark.parametrize(("line", "expected"), [
    ("radius_ip_1=10.0.0.1", "radius_ip_1=10.230.230.1"),
    (
        (
            "        inet 10.0.2.15"
            "  netmask 255.255.255.0"
            "  broadcast 10.0.2.255"
        ),
        (
            "        inet 10.230.230.3"
            "  netmask 10.230.230.1"
            "  broadcast 10.230.230.2"
        ),
    ),
    (
        "radius_ip_1=10.0.0.100-10.0.0.200",
        "radius_ip_1=10.230.230.1-10.230.230.2",
    ),
])
def test_sub_ip_match(line, expected):
    soscleaner = _soscleaner()
    actual = soscleaner._sub_ip(line)
    assert actual == expected


@mark.parametrize(("line", "expected"), [
    (
        (
            "        inet 10.0.2.155"
            "  netmask 10.0.2.1"
            "  broadcast 10.0.2.15"
        ),
        (
            "        inet 10.230.230.1"
            "  netmask 10.230.230.3"
            "  broadcast 10.230.230.2"
        ),
    ),
])
def test_sub_ip_match_IP_overlap(line, expected):
    soscleaner = _soscleaner()
    actual = soscleaner._sub_ip(line)
    assert actual == expected


@mark.parametrize(("line", "expected"), [
    (
        "tcp6       0      0 10.0.0.1:23           10.0.0.110:63564   ESTABLISHED 0",
        "tcp6       0      0 10.230.230.2:23       10.230.230.1:63564 ESTABLISHED 0"
    ),
    (
        "tcp6  10.0.0.11    0 10.0.0.1:23       10.0.0.111:63564    ESTABLISHED 0",
        "tcp6  10.230.230.2 0 10.230.230.3:23   10.230.230.1:63564  ESTABLISHED 0"
    ),
    (
        "unix  2      [ ACC ]     STREAM     LISTENING     43279    2070/snmpd         172.31.0.1\n",
        "unix  2      [ ACC ]     STREAM     LISTENING     43279    2070/snmpd         10.230.230.1\n"
    ),
    (
        "unix  2      [ ACC ]     STREAM     LISTENING     43279    2070/snmpd         172.31.111.11\n",
        "unix  2      [ ACC ]     STREAM     LISTENING     43279    2070/snmpd         10.230.230.1 \n"
    ),
])
def test_sub_ip_match_IP_overlap_netstat(line, expected):
    soscleaner = _soscleaner()
    actual = soscleaner._sub_ip_netstat(line)
    assert actual == expected


@mark.parametrize(("original", "expected"), [
    (
        "{\"name\":\"shadow-utils\","
        "\"epoch\":\"2\","
        "\"version\":\"4.1.5.1\","
        "\"release\":\"5.el6\","
        "\"arch\":\"x86_64\","
        "\"installtime\":\"Wed 13 Jan 2021 10:04:18 AM CET\","
        "\"buildtime\":\"1455012203\","
        "\"vendor\":\"Red Hat, Inc.\","
        "\"buildhost\":\"x86-027.build.eng.bos.redhat.com\","
        "\"sigpgp\":"
        "\"RSA/8, "
        "Tue 08 Mar 2016 11:15:08 AM CET, "
        "Key ID 199e2f91fd431d51\"}",

        "{\"name\":\"shadow-utils\","
        "\"epoch\":\"2\","
        "\"version\":\"10.230.230.1\","
        "\"release\":\"5.el6\","
        "\"arch\":\"x86_64\","
        "\"installtime\":\"Wed 13 Jan 2021 10:04:18 AM CET\","
        "\"buildtime\":\"1455012203\","
        "\"vendor\":\"Red Hat, Inc.\","
        "\"buildhost\":\"x86-027.build.eng.bos.redhat.com\","
        "\"sigpgp\":"
        "\"RSA/8, "
        "Tue 08 Mar 2016 11:15:08 AM CET, "
        "Key ID 199e2f91fd431d51\"}",
    )
])
@patch("insights.contrib.soscleaner.SOSCleaner._ip2db", return_value="10.230.230.1")
def test_sub_ip_false_positive(_ip2db, original, expected):
    soscleaner = _soscleaner()
    actual = soscleaner._sub_ip(original)
    assert actual == expected


def test_excluded_specs():
    soscleaner = SOSCleaner()
    assert len(soscleaner.excluded_specs) > 0
    for spec in soscleaner.excluded_specs:
        assert spec.find("insights.specs.Specs.") == 0


def test_excluded_files():
    report_items = [
        ReportItem(
            "insights.specs.Specs.installed_rpms",
            "insights_commands/rpm_-qa_--qf_name_NAME_epoch_EPOCH_"
            "version_VERSION_release_RELEASE_arch_ARCH_"
            "installtime_INSTALLTIME_date_buildtime_BUILDTIME_"
            "vendor_VENDOR_buildhost_BUILDHOST_sigpgp_SIGPGP_pgpsig"
        ),
        ReportItem(
            "insights.specs.Specs.ip_addr",
            "insights_commands/ip_addr"
        )
    ]

    soscleaner = _soscleaner()
    with _mock_report_dir(report_items) as tmpdir:
        soscleaner.dir_path = tmpdir
        actual = soscleaner._excluded_files()

    expected = [
        report_item.relative_path
        for report_item in report_items
        if report_item.name in soscleaner.excluded_specs
    ]
    assert actual == expected


@patch("insights.contrib.soscleaner.SOSCleaner._clean_file")
@patch("insights.contrib.soscleaner.SOSCleaner._excluded_files")
@patch("insights.contrib.soscleaner.SOSCleaner._extract_sosreport")
@patch("insights.contrib.soscleaner.SOSCleaner._make_dest_env")
@patch("insights.contrib.soscleaner.SOSCleaner._start_logging")
def test_clean_report(
    _start_logging,
    _make_dest_env,
    _extract_sosreport,
    excluded_files,
    clean_file
):
    class FileList:
        def __init__(self, soscleaner):
            self.soscleaner = soscleaner

        def __call__(self, data_path):
            self.soscleaner.file_count = len(file_list_files)

            paths = []
            for file in file_list_files:
                path = join(self.soscleaner.dir_path, data_path, file)
                paths.append(path)
            self.return_value = paths
            return paths

    file_list_files = [
        "insights_commands/rpm_-qa_--qf_name_NAME_version_VERSION",
        "insights_commands/ip_addr"
    ]

    file_list_exempt = file_list_files[0:1]
    excluded_files.configure_mock(return_value=file_list_exempt)

    config = InsightsConfig()
    options = CleanOptions(config, None, None, None)
    options.no_tar_file = "."

    soscleaner = _soscleaner()
    with patch(
        "insights.contrib.soscleaner.SOSCleaner._file_list",
        FileList(soscleaner)
    ) as file_list:
        soscleaner.clean_report(options, ".")

    file_list_whitelisted = file_list.return_value[1:2]
    calls_whitelisted = map(call, file_list_whitelisted)
    assert clean_file.mock_calls == list(calls_whitelisted)
