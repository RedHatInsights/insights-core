from insights.core import IniConfigFile
from insights.tests import context_wrap
from insights.contrib.ConfigParser import NoOptionError
import pytest

# An example config file with a few tricks and traps for the parser
CONFIG_FILE = """
[global]
keynospace=valuenospaces
key with spaces = value with spaces
key with continued value = value1
                           value2
[comment tricks]
; semicolon comment = should not be found
# hash comment = should not be found
comment # in key = value still found
comment in value = value includes # sign

[value overwriting]
key = value1
key = value2
key = value3
key = this one should be picked

#[commented section]
#this key = should not be found either

[value checks]
positive integer value = 14
negative integer value = -993
positive float value = 3.791
negative float value = -91.2e6
true boolean value = yes
false boolean value = off
""".strip()


def test_ini_config_file_parser():
    ini = IniConfigFile(context_wrap(CONFIG_FILE))

    # sections() tests
    assert list(ini.sections()) == \
        ['global', 'comment tricks', 'value overwriting', 'value checks']

    # items() tests - here we return a dictionary
    assert dict(ini.items('global')) == \
        {'keynospace': 'valuenospaces',
         'key with spaces': 'value with spaces',
         'key with continued value': "value1\nvalue2"}
    assert dict(ini.items('comment tricks')) == \
        {'comment # in key': 'value still found',
         'comment in value': 'value includes # sign'}
    assert dict(ini.items('value overwriting')) == \
        {'key': 'this one should be picked'}

    # get() tests on global section
    assert ini.get('global', 'keynospace') == 'valuenospaces'
    assert ini.get('global', 'key with spaces') == 'value with spaces'
    assert ini.get('global', 'key with continued value') == "value1\nvalue2"
    # keys should not appear in other sections, raise NoOptionError
    with pytest.raises(NoOptionError):
        assert ini.get('global', 'key') is None

    # Other comment tricks
    assert ini.get('comment tricks', 'comment # in key') == 'value still found'
    assert ini.get('comment tricks', 'comment in value') == \
        'value includes # sign'

    # Multiple lines giving the same key - last value overwrites.
    assert ini.get('value overwriting', 'key') == 'this one should be picked'

    # getint / getfloat / getboolean tests
    assert ini.getint('value checks', 'positive integer value') == 14
    assert ini.getint('value checks', 'negative integer value') == -993
    assert ini.getfloat('value checks', 'positive float value') == 3.791
    assert ini.getfloat('value checks', 'negative float value') == -91.2e6
    assert ini.getboolean('value checks', 'true boolean value')
    assert not ini.getboolean('value checks', 'false boolean value')

    # positive has_option tests
    assert ini.has_option('global', 'key with spaces')
    assert ini.has_option('comment tricks', 'comment in value')

    # Negative has_option tests:
    # Commented keys
    with pytest.raises(NoOptionError):
        assert ini.get('comment tricks', 'semicolon comment') is None
    assert not ini.has_option('comment tricks', 'semicolon comment')
    with pytest.raises(NoOptionError):
        assert ini.get('comment tricks', 'hash comment') is None
    assert not ini.has_option('comment tricks', 'hash comment')
    # Commented section
    assert not ini.has_option('commented section', 'this key')

    # __contains__ tests
    assert 'global' in ini
    assert 'value checks' in ini
