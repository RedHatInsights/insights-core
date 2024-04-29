from insights.client.config import InsightsConfig
from insights.core.spec_cleaner import Cleaner


def test_get_obfuscate_functions_default_obfuscate_true():
    conf = InsightsConfig(obfuscate=True)
    pp = Cleaner(conf, {})
    assert pp.get_obfuscate_functions() == [pp._sub_ip]

    conf = InsightsConfig(obfuscate=True, obfuscate_hostname=True)
    pp = Cleaner(conf, {})
    assert pp.get_obfuscate_functions() == [pp._sub_ip, pp._sub_hostname]


def test_get_obfuscate_functions_default_obfuscate_false():
    conf = InsightsConfig(obfuscate=False)
    pp = Cleaner(conf, {})
    assert pp.get_obfuscate_functions() == []


def test_get_obfuscate_functions():
    conf = InsightsConfig(obfuscate=True)
    pp = Cleaner(conf, {})
    assert pp.get_obfuscate_functions(filename='test') == [pp._sub_ip]
    assert pp.get_obfuscate_functions(filename='netstat_-neopa') == [pp._sub_ip_netstat]
    assert pp.get_obfuscate_functions(no_obfuscate=['ip']) == []

    conf = InsightsConfig(obfuscate=True, obfuscate_hostname=True)
    pp = Cleaner(conf, {})
    assert pp.get_obfuscate_functions(filename='test') == [pp._sub_ip, pp._sub_hostname]
    assert pp.get_obfuscate_functions(filename='netstat_-neopa') == [pp._sub_ip_netstat, pp._sub_hostname]
    assert pp.get_obfuscate_functions(no_obfuscate=['ip']) == [pp._sub_hostname]
    assert pp.get_obfuscate_functions(no_obfuscate=['ip', 'hostname']) == []
