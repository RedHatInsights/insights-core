from insights.parsers import software_collections_list as parsermodule
from insights.parsers.software_collections_list import SoftwareCollectionsListInstalled
from insights.tests import context_wrap
from doctest import testmod


EXAMPLE_IN_DOCS = """
devtoolset-7
httpd24
python27
rh-mysql57
rh-nodejs8
rh-php71
rh-python36
rh-ruby24
"""

EXAMPLE_WITH_EMPTY_LINES = """
devtoolset-7
httpd24

python27
rh-mysql57

rh-nodejs8
rh-php71
rh-python36

rh-ruby24
"""

EXAMPLE_WITH_SPACES = """
        devtoolset-7  \t
httpd24
python27   \t
rh-mysql57   \t
  rh-nodejs8  \t
rh-php71
rh-python36
rh-ruby24   \n
"""

EXAMPLE_EMPTY = ''

COLLECTIONS_LIST = [
    'devtoolset-7',
    'httpd24',
    'python27',
    'rh-mysql57',
    'rh-nodejs8',
    'rh-php71',
    'rh-python36',
    'rh-ruby24',
]


def _assert_collections(coll_parser, coll_list):
    assert coll_parser.records == coll_list
    for coll in coll_list:
        assert coll_parser.exists(coll)


def test_module_documentation():
    failed, total = testmod(parsermodule, globs={
        "collections": SoftwareCollectionsListInstalled(context_wrap(EXAMPLE_IN_DOCS))
    })
    assert failed == 0


def test_swcol_parsing():

    scls = SoftwareCollectionsListInstalled(context_wrap(EXAMPLE_IN_DOCS))
    _assert_collections(scls, COLLECTIONS_LIST)


def test_swcol_exceptions_in_input():
    # Empty lines should be handled properly.
    scls = SoftwareCollectionsListInstalled(context_wrap(EXAMPLE_WITH_EMPTY_LINES))
    _assert_collections(scls, COLLECTIONS_LIST)
    assert not scls.exists('foo')
    # Spaces at beginning and at the end of lines should be handled properly.
    scls = SoftwareCollectionsListInstalled(context_wrap(EXAMPLE_WITH_SPACES))
    _assert_collections(scls, COLLECTIONS_LIST)
    assert not scls.exists('bar')
    # With empty input parser does not contain any records.
    scls = SoftwareCollectionsListInstalled(context_wrap(EXAMPLE_EMPTY))
    _assert_collections(scls, [])
    assert not scls.exists('rh-joke')
