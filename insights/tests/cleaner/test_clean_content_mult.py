from insights.cleaner import Cleaner
from insights.client.config import InsightsConfig


def test_obfuscate_hostname_and_ip():
    hostname = 'test1.abc.com'
    line = "test1.abc.com, 10.0.0.1 test1.abc.loc, 20.1.4.7 smtp.abc.com, 10.1.2.7 lite.abc.com"
    c = InsightsConfig(obfuscate=True, obfuscate_hostname=True, hostname=hostname)
    pp = Cleaner(c, {}, hostname)
    result = pp.clean_content(line)
    assert 'example.com' in result
    assert '10.230.230' in result
    for item in line.split():
        assert item not in result


def test_clean_content_keyword_with_hostname_and_ip():
    hostname = 'test1.abc.com'
    line = "test1.abc.com, 10.0.0.1, test1.abc.loc, 20.1.4.7, smtp.abc.com, what's your name?, what day is today?"
    conf = InsightsConfig(obfuscate=True, obfuscate_hostname=True, hostname=hostname)
    pp = Cleaner(conf, {'keywords': ['name', 'day']}, hostname)
    result = pp.clean_content(line)
    assert 'test1.abc.com' not in result
    assert '10.0.0.1' not in result
    assert '20.1.4.7' not in result
    assert 'name' not in result
    assert 'day' not in result
    assert 'keyword0' in result
    assert 'keyword1' in result
