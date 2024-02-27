import csv
import json
import os

from mock.mock import patch
from pytest import mark

from insights.client.archive import InsightsArchive
from insights.client.config import InsightsConfig
from insights.core.spec_cleaner import Cleaner

hostname = "report.test.com"
test_file_data = 'ip: 10.0.2.155\ntestword\n{0}'.format(hostname)


@mark.parametrize(
    ("obfuscate", "obfuscate_hostname"),
    [
        (False, False), (True, False), (True, True),
    ]
)
@mark.parametrize("core_collect", [True, False])
@mark.parametrize("test_umask", [0o000, 0o022])
def test_rhsm_facts(test_umask, core_collect, obfuscate, obfuscate_hostname):
    rhsm_facts_file = '/tmp/insights_test_rhsm.facts'
    conf = InsightsConfig(core_collect=core_collect, obfuscate=obfuscate,
                          obfuscate_hostname=obfuscate_hostname)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    # put something in the archive to redact
    test_file = os.path.join(arch.archive_dir, 'test.file')
    with open(test_file, 'w') as t:
        t.write(test_file_data)

    old_umask = os.umask(test_umask)
    pp = Cleaner(conf, {'keywords': ['testword']}, hostname)
    pp.clean_file(test_file, [])
    pp.generate_report(arch.archive_name, rhsm_facts_file)
    arch.delete_archive_dir()

    umask_after_test = os.umask(old_umask)

    assert os.path.isfile(rhsm_facts_file)
    st = os.stat(rhsm_facts_file)
    assert st.st_mode & 0o777 == 0o644 & ~test_umask
    assert umask_after_test == test_umask  # umask was not changed by Cleaner
    with open(rhsm_facts_file, 'r') as fp:
        facts = json.load(fp)
        # hostname
        assert facts['insights_client.hostname'] == hostname
        assert facts['insights_client.obfuscate_hostname_enabled'] == obfuscate_hostname
        hns = json.loads(facts['insights_client.hostnames'])
        if obfuscate_hostname:
            assert hns[0]['original'] == hostname
            assert '.example.com' in hns[0]['obfuscated']
        else:
            hns == []
        # ip
        assert facts['insights_client.obfuscate_ip_enabled'] == obfuscate
        ips = json.loads(facts['insights_client.ips'])
        if obfuscate:
            assert ips[0]['original'] == '10.0.2.155'
            assert ips[0]['obfuscated'] == '10.230.230.1'
        else:
            assert ips == []
        # keyword
        kws = json.loads(facts['insights_client.keywords'])
        assert kws[0]['original'] == 'testword'
        assert kws[0]['obfuscated'] == 'keyword0'

    os.unlink(rhsm_facts_file)


@mark.parametrize("rm_conf", [{}, {'keywords': ['testword']}])
@mark.parametrize(
    ("obfuscate", "obfuscate_hostname"),
    [
        (False, False), (True, False), (True, True),
    ]
)
@mark.parametrize("core_collect", [True, False])
@patch('insights.core.spec_cleaner.Cleaner.generate_rhsm_facts', return_value=None)
def test_all_csv_reports(rhsm_facts, core_collect, obfuscate, rm_conf, obfuscate_hostname):
    conf = InsightsConfig(core_collect=core_collect, obfuscate=obfuscate,
                          obfuscate_hostname=obfuscate_hostname)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    # put something in the archive to redact
    test_file = os.path.join(arch.archive_dir, 'test.file')
    with open(test_file, 'w') as t:
        t.write(test_file_data)

    pp = Cleaner(conf, rm_conf, hostname)
    ip_report_file = os.path.join(pp.report_dir, "%s-ip.csv" % arch.archive_name)
    hn_report_file = os.path.join(pp.report_dir, "%s-hostname.csv" % arch.archive_name)
    kw_report_file = os.path.join(pp.report_dir, "%s-keyword.csv" % arch.archive_name)
    if os.path.isfile(ip_report_file):
        os.unlink(ip_report_file)
    if os.path.isfile(hn_report_file):
        os.unlink(hn_report_file)
    if os.path.isfile(kw_report_file):
        os.unlink(kw_report_file)

    pp.clean_file(test_file, [])
    pp.generate_report(arch.archive_name, '/dev/null')
    arch.delete_archive_dir()

    if obfuscate:
        assert os.path.isfile(ip_report_file)
        with open(ip_report_file, 'r') as fp:
            ips = list(csv.reader(fp.readlines(), skipinitialspace=True))
            # ip
            assert len(ips) > 1
            assert ips[0] == ['Obfuscated IP', 'Original IP']
            assert ips[1] == ['10.230.230.1', '10.0.2.155']
        os.unlink(ip_report_file)
    else:
        assert not os.path.isfile(ip_report_file)

    if obfuscate_hostname:
        assert os.path.isfile(hn_report_file)
        with open(hn_report_file, 'r') as fp:
            hns = list(csv.reader(fp.readlines(), skipinitialspace=True))
            # hn
            assert len(hns) > 1
            assert hns[0] == ['Obfuscated Hostname', 'Original Hostname']
            assert hns[1] == ['f9fe0db0c046.example.com', 'report.test.com']
        os.unlink(hn_report_file)
    else:
        assert not os.path.isfile(hn_report_file)

    if rm_conf:
        assert os.path.isfile(kw_report_file)
        with open(kw_report_file, 'r') as fp:
            kws = list(csv.reader(fp.readlines(), skipinitialspace=True))
            # kw
            assert len(kws) > 1
            assert kws[0] == ['Replaced Keyword', 'Original Keyword']
            assert kws[1] == ['testword', 'keyword0']
        os.unlink(kw_report_file)
    else:
        assert not os.path.isfile(kw_report_file)
