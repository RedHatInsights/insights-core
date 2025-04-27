import os
from collections import defaultdict

import pytest
from mock.mock import patch

from insights.core import dr
from insights.core import filters
from insights.core.context import HostArchiveContext
from insights.core.filters import add_filter
from insights.core.hydration import initialize_broker
from insights.core.spec_factory import RegistryPoint, SpecSet, simple_file

SAMPLE_FILE = "sample_file.log"
FILTER_DATA = "Some test data"
filter_kw = '9Some'
CONTENT_LINES = 1000


class Specs(SpecSet):
    large_file = RegistryPoint(filterable=False)
    large_file_wf = RegistryPoint(filterable=True)


class Stuff(Specs):
    large_file = simple_file(SAMPLE_FILE, context=HostArchiveContext)
    large_file_wf = simple_file(SAMPLE_FILE, context=HostArchiveContext)


class stage(dr.ComponentType):
    def invoke(self, broker):
        return self.component(broker)


@stage(Stuff.large_file, Stuff.large_file_wf)
def dostuff(broker):
    assert Stuff.large_file in broker
    assert Stuff.large_file_wf in broker


@pytest.fixture()
def reset_filters():
    original_cache = filters._CACHE
    original_filters = filters.FILTERS
    filters._CACHE = {}
    filters.FILTERS = defaultdict(dict)
    yield
    filters._CACHE = original_cache
    filters.FILTERS = original_filters


@pytest.fixture(scope="module")
def sample_file(tmpdir_factory):
    root = str(tmpdir_factory.mktemp("test_content_provider_load"))
    relpath = SAMPLE_FILE
    file_path = os.path.join(root, relpath)
    with open(file_path, 'w') as fd:
        for i in range(CONTENT_LINES):
            fd.write('- ' + str(i) + FILTER_DATA + '\n')
    return root, relpath


@patch('insights.core.spec_factory.MAX_CONTENT_SIZE', 1024)
@patch('insights.core.spec_factory.log')
@pytest.mark.parametrize(
    "spec, filters, expected_first_line, expected_lines",
    [
        (Stuff.large_file, [], "- 949Some test data", 51),
        (Stuff.large_file_wf, ["9Some"], "- 949Some test data", 6),
    ]
)
def test_load(log, reset_filters, sample_file, spec, filters, expected_first_line, expected_lines):
    root, relpath = sample_file

    for filter_kw in filters:
        add_filter(spec, filter_kw)

    _, broker = initialize_broker(root, context=HostArchiveContext, broker=dr.Broker())
    broker = dr.run(dr.get_dependency_graph(dostuff), broker=broker)

    assert spec in broker
    assert broker[spec].content[0] == expected_first_line
    assert len(broker[spec].content) == expected_lines
    log.debug.assert_called_with("Extra-huge file is truncated %s", SAMPLE_FILE)
