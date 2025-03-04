from mock.mock import patch

from insights.cleaner import Cleaner
from insights.client.config import InsightsConfig

hostname = 'test1.abc.com'
line = "test1.abc.com, 10.0.0.1 test1.abc.loc 20.1.4.7 smtp.abc.com 10.1.2.7 lite.abc.com"


@patch("insights.cleaner.MAX_LINE_LENGTH", len(hostname) + 1)
def test_max_line_length_less():
    c = InsightsConfig(obfuscate=True, obfuscate_hostname=True, hostname=hostname)
    pp = Cleaner(c, {}, hostname)
    result = pp.clean_content(line)
    assert 'example.com' in result
    assert '10.230.230' not in result
    assert result[-1] == ','


@patch("insights.cleaner.MAX_LINE_LENGTH", len(line) + 10)
def test_max_line_length_greater():
    c = InsightsConfig(obfuscate=True, obfuscate_hostname=True, hostname=hostname)
    pp = Cleaner(c, {}, hostname)
    result = pp.clean_content(line)
    assert 'example.com' in result
    assert '10.230.230' in result
    assert result.endswith('example.com')
