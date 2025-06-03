import csv
import json
import os

from mock.mock import patch
from pytest import mark

from insights.client.archive import InsightsArchive
from insights.client.config import InsightsConfig
from insights.cleaner import Cleaner
from insights.cleaner.utilities import write_report

hostname = "report.test.com"
test_file_data = '{0}'.format(hostname)
test_file_data += 'testword\n'
test_file_data += 'ipv4: 10.0.2.155\n'
test_file_data += 'ipv6: abcd::1\n'
test_file_data += 'mac: 10:20:02:15:f5:ab'


@mark.parametrize(
    ("obfuscate", "obfuscate_hostname", "obfuscation_list", "keywords"),
    [
        (False, False, None, []),
        (True, False, None, []),
        (True, True, None, []),
        (True, True, None, ['testword']),
        (None, None, 'ipv4, mac', []),
        (None, None, 'ipv6, hostname', []),
        (None, None, 'ipv4, ipv6, hostname, mac', ['testword']),
    ],
)
@mark.parametrize("test_umask", [0o000, 0o022])
def test_rhsm_facts(test_umask, obfuscate, obfuscate_hostname, obfuscation_list, keywords):
    rhsm_facts_file = '/tmp/insights_test_rhsm.facts'
    conf = InsightsConfig(
        obfuscate=obfuscate,
        obfuscate_hostname=obfuscate_hostname,
        obfuscation_list=obfuscation_list,
    )
    conf.rhsm_facts_file = rhsm_facts_file
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    # put something in the archive to redact
    test_file = os.path.join(arch.archive_dir, 'test.file')
    with open(test_file, 'w') as t:
        t.write(test_file_data)

    old_umask = os.umask(test_umask)
    pp = Cleaner(conf, {'keywords': keywords}, hostname)
    pp.clean_file(test_file, [])
    pp.generate_report(arch.archive_name)
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
        assert facts['insights_client.obfuscate_hostname_enabled'] == bool(
            obfuscate_hostname or obfuscation_list and 'hostname' in obfuscation_list
        )
        hns = json.loads(facts['insights_client.obfuscated_hostname'])
        if obfuscate_hostname or obfuscation_list and 'hostname' in obfuscation_list:
            assert hns[0]['original'] == hostname
            assert '.example.com' in hns[0]['obfuscated']
            assert len(hns[0]['obfuscated'].split('.', 1)[0]) == 12
        else:
            assert hns == []
        # ip
        assert facts['insights_client.obfuscate_ipv4_enabled'] == bool(
            obfuscate or obfuscation_list and 'ipv4' in obfuscation_list
        )
        ips = json.loads(facts['insights_client.obfuscated_ipv4'])
        if obfuscate or obfuscation_list and 'ipv4' in obfuscation_list:
            assert ips[0]['original'] == '10.0.2.155'
            assert ips[0]['obfuscated'] == '10.230.230.1'
        else:
            assert ips == []
        # ipv6
        assert facts['insights_client.obfuscate_ipv6_enabled'] == bool(
            obfuscation_list and 'ipv6' in obfuscation_list
        )
        ips = json.loads(facts['insights_client.obfuscated_ipv6'])
        if obfuscation_list and 'ipv6' in obfuscation_list:
            assert ips[0]['original'] == 'abcd::1'
            assert ips[0]['obfuscated'] != 'abcd::1'
            assert len(ips[0]['obfuscated']) == len('abcd::1')
        else:
            assert ips == []
        # mac
        assert facts['insights_client.obfuscate_mac_enabled'] == bool(
            obfuscation_list and 'mac' in obfuscation_list
        )
        macs = json.loads(facts['insights_client.obfuscated_mac'])
        if obfuscation_list and 'mac' in obfuscation_list:
            assert macs[0]['original'] == '10:20:02:15:f5:ab'
            assert macs[0]['obfuscated'] == 'b1:91:bc:f1:54:da'
        else:
            assert macs == []
        # keyword
        kws = json.loads(facts['insights_client.obfuscated_keyword'])
        if keywords:
            assert kws[0]['original'] == 'testword'
            assert kws[0]['obfuscated'] == 'keyword0'
        else:
            assert kws == []

    os.unlink(rhsm_facts_file)


@mark.parametrize(
    ("obfuscate", "obfuscate_hostname", "obfuscation_list", "keywords"),
    [
        (False, False, None, []),
        (True, False, None, []),
        (True, True, None, []),
        (True, True, None, ['testword']),
        (None, None, 'ipv4, mac', []),
        (None, None, 'ipv6, hostname', []),
        (None, None, 'ipv4, ipv6, hostname, mac', ['testword']),
    ],
)
@patch('insights.cleaner.Cleaner.generate_rhsm_facts', return_value=None)
def test_all_csv_reports(rhsm_facts, obfuscate, obfuscate_hostname, obfuscation_list, keywords):
    conf = InsightsConfig(
        obfuscate=obfuscate,
        obfuscate_hostname=obfuscate_hostname,
        obfuscation_list=obfuscation_list,
    )
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    # put something in the archive to redact
    test_file = os.path.join(arch.archive_dir, 'test.file')
    with open(test_file, 'w') as t:
        t.write(test_file_data)

    pp = Cleaner(conf, {'keywords': keywords}, hostname)
    ip_report_file = os.path.join(pp.report_dir, "%s-ipv4.csv" % arch.archive_name)
    ipv6_report_file = os.path.join(pp.report_dir, "%s-ipv6.csv" % arch.archive_name)
    hn_report_file = os.path.join(pp.report_dir, "%s-hostname.csv" % arch.archive_name)
    kw_report_file = os.path.join(pp.report_dir, "%s-keyword.csv" % arch.archive_name)
    mac_report_file = os.path.join(pp.report_dir, "%s-mac.csv" % arch.archive_name)
    if os.path.isfile(ip_report_file):
        os.unlink(ip_report_file)
    if os.path.isfile(ipv6_report_file):
        os.unlink(ipv6_report_file)
    if os.path.isfile(hn_report_file):
        os.unlink(hn_report_file)
    if os.path.isfile(kw_report_file):
        os.unlink(kw_report_file)
    if os.path.isfile(mac_report_file):
        os.unlink(mac_report_file)

    pp.clean_file(test_file, [])
    pp.generate_report(arch.archive_name)
    arch.delete_archive_dir()

    if obfuscate or obfuscation_list and 'ipv4' in obfuscation_list:
        assert os.path.isfile(ip_report_file)
        with open(ip_report_file, 'r') as fp:
            ips = list(csv.reader(fp.readlines(), skipinitialspace=True))
            # ip
            assert len(ips) > 1
            assert ips[0] == ['Obfuscated IPv4', 'Original IPv4']
            assert ips[1] == ['10.230.230.1', '10.0.2.155']
        os.unlink(ip_report_file)
    else:
        assert not os.path.isfile(ip_report_file)
    if obfuscation_list and 'ipv6' in obfuscation_list:
        assert os.path.isfile(ipv6_report_file)
        with open(ipv6_report_file, 'r') as fp:
            ips = list(csv.reader(fp.readlines(), skipinitialspace=True))
            # ipv6
            assert len(ips) > 1
            assert ips[0] == ['Obfuscated IPv6', 'Original IPv6']
            assert ips[1][1] == 'abcd::1'
            assert ips[1][0] != ips[1][1]
            assert len(ips[1][0]) == len(ips[1][1])
        os.unlink(ipv6_report_file)
    else:
        assert not os.path.isfile(ipv6_report_file)

    if obfuscate_hostname or obfuscation_list and 'hostname' in obfuscation_list:
        assert os.path.isfile(hn_report_file)
        with open(hn_report_file, 'r') as fp:
            hns = list(csv.reader(fp.readlines(), skipinitialspace=True))
            # hn
            assert len(hns) > 1
            assert hns[0] == ['Obfuscated Hostname', 'Original Hostname']
            assert len(hns[1][0].split('.', 1)[0]) == 12
        os.unlink(hn_report_file)
    else:
        assert not os.path.isfile(hn_report_file)

    if obfuscation_list and 'mac' in obfuscation_list:
        assert os.path.isfile(mac_report_file)
        with open(mac_report_file, 'r') as fp:
            hns = list(csv.reader(fp.readlines(), skipinitialspace=True))
            # hn
            assert len(hns) > 1
            assert hns[0] == ['Obfuscated MAC', 'Original MAC']
            assert hns[1] == ['b1:91:bc:f1:54:da', '10:20:02:15:f5:ab']
        os.unlink(mac_report_file)
    else:
        assert not os.path.isfile(hn_report_file)

    if keywords:
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


def test_wirte_report_exp():
    report_file = '/tmp/_test.csv'
    write_report(None, report_file)
    os.unlink(report_file)
