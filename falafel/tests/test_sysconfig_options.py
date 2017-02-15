# -*- coding: UTF-8 -*-
from falafel.core import SysconfigOptions
from falafel.tests import context_wrap
import unittest


STANDARD_CONFIG = """
# This is a standard, but made up, config file example
OPTIONS="-x -g"

USER=root
HOST=192.168.0.100
PORT=1066
"""


TRICKY_CONFIG = """
# COMMENTED_OUT=1
SELECTOR='and all that'
     SPACES_IN_FRONT=yes
COMMENT_SPACE_OK=value_with_#
SPACE_COMMENT_IGNORED=value_with #nothing else
COMMENT_NOSPACE_OK=value_with_#_in_it
COMMENT_QUOTED_IN_VALUE="This value should have a # character in it"
MANY_QUOTES="this "'is'" valid"
QUOTE_HANDLING="single ' allowed"
OPTION_WITH_NO_VALUE=
  # blank lines with a comment are ignored

# blank lines without comments are ignored too.
this line should be in unparsed lines afterward
AND = 'so should this'
""" + "SPACES_AFTER_VALUE=should_be_ignored    \n" + "  \n"


class Sysconfigdockercheck(unittest.TestCase):
    def test_standard_config(self):
        config = SysconfigOptions(context_wrap(STANDARD_CONFIG))

        assert 'OPTIONS' in config.data
        assert 'USER' in config.data
        assert 'HOST' in config.data
        assert 'PORT' in config.data

        print config.data

        assert config.data['OPTIONS'] == '-x -g'
        assert config.data['USER'] == 'root'
        assert config.data['HOST'] == '192.168.0.100'
        assert config.data['PORT'] == '1066'

    def test_tricky_config(self):
        config = SysconfigOptions(context_wrap(TRICKY_CONFIG))

        print config.data.keys()
        assert sorted(config.data.keys()) == sorted([
            'SELECTOR', 'SPACES_IN_FRONT', 'SPACES_AFTER_VALUE',
            'COMMENT_SPACE_OK', 'SPACE_COMMENT_IGNORED', 'COMMENT_NOSPACE_OK',
            'COMMENT_QUOTED_IN_VALUE', 'MANY_QUOTES', 'QUOTE_HANDLING',
            'OPTION_WITH_NO_VALUE'])

        assert config.data['SELECTOR'] == 'and all that'
        assert config.data['SPACES_IN_FRONT'] == 'yes'
        assert config.data['SPACES_AFTER_VALUE'] == 'should_be_ignored'
        assert config.data['COMMENT_SPACE_OK'] == 'value_with_#'
        assert config.data['SPACE_COMMENT_IGNORED'] == 'value_with'
        assert config.data['COMMENT_NOSPACE_OK'] == 'value_with_#_in_it'
        assert config.data['COMMENT_QUOTED_IN_VALUE'] == \
            "This value should have a # character in it"
        assert config.data['MANY_QUOTES'] == "this is valid"
        assert config.data['QUOTE_HANDLING'] == "single ' allowed"
        assert config.data['OPTION_WITH_NO_VALUE'] == ''

        print config.unparsed_lines
        assert config.unparsed_lines == [
            'this line should be in unparsed lines afterward',
            "AND = 'so should this'",
        ]
