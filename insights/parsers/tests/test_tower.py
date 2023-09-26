import pytest
from insights.parsers.tower import TowerVersion
from insights.tests import context_wrap

OKAY = """
3.4.0
"""

OKAY_NO_NEWLINE = '3.4.0'


@pytest.mark.parametrize('tower_version_file_contents', [OKAY, OKAY_NO_NEWLINE])
def test_ok(tower_version_file_contents):
    tv = TowerVersion(context_wrap(tower_version_file_contents))
    assert '3.4.0' == tv.version

