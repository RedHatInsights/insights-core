from mock.mock import patch

from insights.client.config import InsightsConfig
from insights.cleaner import Cleaner


def test_obfuscate_hostname():
    hostname = 'test1.abc.com'
    line = "a line with %s here, test2.abc.com, test.redhat.com" % hostname
    c = InsightsConfig(obfuscate=True, obfuscate_hostname=True, hostname=hostname)
    pp = Cleaner(c, {}, hostname)
    actual = pp.clean_content(line)
    assert 'test1' not in actual
    assert 'test2' not in actual
    assert 'abc.com' not in actual
    assert len(actual.split('.example.com')[0].split()[-1]) == 12
    assert len(actual.split('.example.com')[1].split()[-1]) == 12
    assert '.example.com' in actual
    assert 'host' not in actual

    line = "a line w/o hostname, but test2.abc.com only"
    actual = pp.clean_content(line)
    assert 'test2' not in actual
    assert 'abc.com' not in actual
    assert '.example.com' in actual
    assert len(actual.split('.example.com')[0].split()[-1]) == 12

    hostname = 'test1'  # Short hostname
    line = "a line with %s here, test2.def.com" % hostname
    pp = Cleaner(c, {}, hostname)
    actual = pp.clean_content(line)
    assert hostname not in actual
    assert 'test2.def.com' in actual

    line = "a line w/o hostname"
    hostname = 'test1.abc.com'
    pp = Cleaner(c, {}, hostname)
    actual = pp.clean_content(line)
    assert line == actual


@patch("insights.cleaner.determine_hostname", return_value='test1.abc.com')
def test_obfuscate_hostname_determine_hostanme(hn):
    hostname = 'test1.abc.com'
    c = InsightsConfig(obfuscate=True, obfuscate_hostname=True, display_name='disp.abc.com')
    line = "a line with %s here, test2.def.com" % hostname
    pp = Cleaner(c, {})  # passed empty hostname to cleaner, determain it
    actual = pp.clean_content(line)
    assert hostname not in actual
    assert len(actual.split('.')[0].split()[-1]) == 12
    assert 'test2.def.com' in actual


@patch("insights.cleaner.determine_hostname", return_value='test1.abc.com')
def test_obfuscate_hostname_empty_line(hn):
    c = InsightsConfig(obfuscate=True, obfuscate_hostname=True, display_name='disp.abc.com')
    line = ""
    pp = Cleaner(c, {})  # passed empty hostname to cleaner, determain it
    actual = pp.clean_content(line)
    assert actual == line
