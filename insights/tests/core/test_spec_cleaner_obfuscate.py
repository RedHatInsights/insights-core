# -*- coding: utf-8 -*-
import os

from mock.mock import patch
from pytest import mark

from insights.client.archive import InsightsArchive
from insights.client.config import InsightsConfig
from insights.core.spec_cleaner import Cleaner


@mark.parametrize(("line", "expected"), [
    ("test_no_ip", "test_no_ip"),
    ("test 127.0.0.1", "test 127.0.0.1"),
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
def test_obfuscate_ip_match(line, expected):
    c = InsightsConfig(obfuscate=True)
    pp = Cleaner(c, {})
    actual = pp._obfuscate_line(line, [pp._sub_ip])
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
def test_obfuscate_ip_match_IP_overlap(line, expected):
    c = InsightsConfig(obfuscate=True)
    pp = Cleaner(c, {})
    actual = pp._obfuscate_line(line, [pp._sub_ip])
    assert actual == expected


@mark.parametrize(("line", "expected"), [
    ("test_no_ip", "test_no_ip"),
    ("test 127.0.0.1", "test 127.0.0.1"),
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
def test_obfuscate_ip_match_IP_overlap_netstat(line, expected):
    c = InsightsConfig(obfuscate=True)
    pp = Cleaner(c, {})
    actual1 = pp._obfuscate_line(line, [pp._sub_ip_netstat])
    actual2 = pp._obfuscate_line(line, [pp._sub_ip_netstat])
    assert actual1 == expected
    assert actual2 == expected


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
@patch("insights.core.spec_cleaner.Cleaner._ip2db", return_value="10.230.230.1")
def test_obfuscate_ip_false_positive(_ip2db, original, expected):
    c = InsightsConfig(obfuscate=True)
    pp = Cleaner(c, {})
    actual = pp._obfuscate_line(original, [pp._sub_ip])
    assert actual == expected
    # BUT works well without "obfuscate=['ip']
    actual = pp._obfuscate_line(original, [])
    assert actual == original


def test_obfuscate_hostname():
    hostname = 'test1.abc.com'
    line = "a line with %s here, test2.abc.com, test.redhat.com" % hostname
    c = InsightsConfig(obfuscate=True, obfuscate_hostname=True, hostname=hostname)
    pp = Cleaner(c, {}, hostname)
    actual = pp._obfuscate_line(line, [pp._sub_hostname])
    assert 'test1' not in actual
    assert 'test2' not in actual
    assert 'abc.com' not in actual
    assert len(actual.split('.')[0].split()[-1]) == 12
    assert '.example.com' in actual

    line = "a line w/o hostname, but test2.abc.com only"
    actual = pp._obfuscate_line(line, [pp._sub_hostname])
    assert 'test2' not in actual
    assert 'abc.com' not in actual
    assert '.example.com' in actual
    assert len(actual.split('.')[0].split()[-1]) != 12

    hostname = 'test1'  # Short hostname
    line = "a line with %s here, test2.def.com" % hostname
    pp = Cleaner(c, {}, hostname)
    actual = pp._obfuscate_line(line, [pp._sub_hostname])
    assert hostname not in actual
    assert 'test2.def.com' in actual

    line = "a line w/o hostname"
    hostname = 'test1.abc.com'
    pp = Cleaner(c, {}, hostname)
    actual = pp._obfuscate_line(line, [pp._sub_hostname])
    assert line == actual


@patch("insights.core.spec_cleaner.determine_hostname", return_value='test1.abc.com')
def test_obfuscate_hostname_determine_hostanme(hn):
    hostname = 'test1.abc.com'
    c = InsightsConfig(obfuscate=True, obfuscate_hostname=True, display_name='disp.abc.com')
    line = "a line with %s here, test2.def.com" % hostname
    pp = Cleaner(c, {})  # passed empty hostname to cleaner, determain it
    actual = pp._obfuscate_line(line, [pp._sub_hostname])
    assert hostname not in actual
    assert len(actual.split('.')[0].split()[-1]) == 12
    assert 'test2.def.com' in actual


@patch("insights.core.spec_cleaner.determine_hostname", return_value='dt_test.abc.com')
def test_cleaner_fqdn(de_hn):
    fqdn = 'test.abc.com'
    c = InsightsConfig(obfuscate=True, obfuscate_hostname=True, display_name='disp.abc.com')
    pp = Cleaner(c, {}, fqdn)  # pass fqdn to cleaner
    assert pp.fqdn == fqdn
    assert len(pp.obfuscated_fqdn.split('.')[0]) == 12

    fqdn1 = 'test.def.com'
    pp = Cleaner(c, {}, fqdn1)  # pass fqdn1 to cleaner
    assert pp.fqdn == fqdn1
    assert len(pp.obfuscated_fqdn.split('.')[0]) == 12

    pp = Cleaner(c, {})  # pass None "hostname" to cleaner
    assert pp.fqdn == "dt_test.abc.com"  # get hostname from determine_hostname, but not display_name
    assert len(pp.obfuscated_fqdn.split('.')[0]) == 12


def test_obfuscate_hostname_and_ip():
    hostname = 'test1.abc.com'
    line = "test1.abc.com, 10.0.0.1 test1.abc.loc, 20.1.4.7 smtp.abc.com, 10.1.2.7 lite.abc.com"
    c = InsightsConfig(obfuscate=True, obfuscate_hostname=True, hostname=hostname)
    pp = Cleaner(c, {}, hostname)
    result = pp._obfuscate_line(line, [pp._sub_ip, pp._sub_hostname])
    assert 'example.com' in result
    assert '10.230.230' in result
    for item in line.split():
        assert item not in result


def test_clean_file_obfuscate():
    conf = InsightsConfig(obfuscate=True)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    # netstat_-neopa
    line = "tcp6       0      0 10.0.0.1:23           10.0.0.110:63564   ESTABLISHED 0"
    ret = "tcp6       0      0 10.230.230.2:23       10.230.230.1:63564 ESTABLISHED 0"

    test_dir = os.path.join(arch.archive_dir, 'data', 'etc')
    os.makedirs(test_dir)
    pp = Cleaner(conf, {})

    # netstat
    test_file = os.path.join(arch.archive_dir, 'data', 'testfile.netstat_-neopa')
    with open(test_file, 'w') as t:
        t.write(line)
    pp.clean_file(test_file, no_obfuscate=[])
    # file is changed per netstat logic
    with open(test_file, 'r') as t:
        assert ret == ''.join(t.readlines())

    arch.delete_archive_dir()


def test_clean_file_obfuscate_disabled_by_no_obfuscate():
    conf = InsightsConfig(obfuscate=True)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    # netstat_-neopa
    line = "tcp6       0      0 10.0.0.1:23           10.0.0.110:63564   ESTABLISHED 0"

    test_dir = os.path.join(arch.archive_dir, 'data', 'etc')
    os.makedirs(test_dir)
    pp = Cleaner(conf, {})

    # netstat
    test_file = os.path.join(arch.archive_dir, 'data', 'testfile.netstat_-neopa')
    with open(test_file, 'w') as t:
        t.write(line)
    pp.clean_file(test_file, no_obfuscate=['ip'])
    # file is NOT changed
    with open(test_file, 'r') as t:
        assert line == ''.join(t.readlines())

    arch.delete_archive_dir()


@patch("insights.core.spec_cleaner.Cleaner._redact_line")
def test_clean_file_non_exist(redact_func):
    conf = InsightsConfig(obfuscate=True)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()

    test_dir = os.path.join(arch.archive_dir, 'data', 'etc')
    os.makedirs(test_dir)
    pp = Cleaner(conf, {})

    pp.clean_file('non_existing_file', no_obfuscate=[])
    redact_func.assert_not_called()

    # empty file
    test_file = os.path.join(arch.archive_dir, 'data', 'etc', 'x.conf')
    with open(test_file, 'w'):
        pass
    pp.clean_file(test_file, no_obfuscate=[])
    redact_func.assert_not_called()

    arch.delete_archive_dir()
