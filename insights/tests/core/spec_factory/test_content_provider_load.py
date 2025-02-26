import os
import shutil
import tempfile

from insights.core import dr
from insights.core.context import HostArchiveContext
from insights.core.filters import add_filter
from insights.core.hydration import initialize_broker
from insights.core.spec_factory import RegistryPoint, SpecSet, MAX_CONTENT_LINES, simple_file

test_large_file = "large_file"
test_large_file_wf = "large_file_with_filter"
FILTER_DATA = "Some test data"
filter_kw = '9Some'


class Specs(SpecSet):
    large_file = RegistryPoint(filterable=False)
    large_file_wf = RegistryPoint(filterable=True)


class Stuff(Specs):
    large_file = simple_file(test_large_file, context=HostArchiveContext)
    large_file_wf = simple_file(test_large_file_wf, context=HostArchiveContext)


class stage(dr.ComponentType):
    def invoke(self, broker):
        return self.component(broker)


@stage(Stuff.large_file, Stuff.large_file_wf)
def dostuff(broker):
    assert Stuff.large_file in broker
    assert Stuff.large_file_wf in broker


def test_load():
    add_filter(Stuff.large_file_wf, filter_kw)
    temp_dir = tempfile.mkdtemp(prefix='insights_test', suffix='.dir')
    os.mkdir(os.path.join(temp_dir, 'data'))

    # Create files with more lines than MAX_CONTENT_LINES in archive/data
    file_path = os.path.join(temp_dir, 'data', test_large_file)
    with open(file_path, 'w') as fd:
        for i in range(MAX_CONTENT_LINES + 10):
            fd.write(str(i) + FILTER_DATA + '\n')

    file_path = os.path.join(temp_dir, 'data', test_large_file_wf)
    with open(file_path, 'w') as fd:
        for i in range(MAX_CONTENT_LINES + 10):
            fd.write(str(i) + FILTER_DATA + '\n')

    # Rules
    dr.load_components('insights.tests.core.spec_factory', continue_on_error=False, exclude=None)

    _, broker = initialize_broker(temp_dir, context=HostArchiveContext, broker=dr.Broker())
    broker = dr.run(dr.get_dependency_graph(dostuff), broker=broker)

    assert Stuff.large_file in broker
    # Only MAX_CONTENT_LINES lines are loaded
    assert len(broker[Stuff.large_file].content) == MAX_CONTENT_LINES
    # Less lines are load due to  MAX_CONTENT_LINES limit and filter
    assert len(broker[Stuff.large_file_wf].content) <= len(
        [
            '{0}{1}'.format(i, FILTER_DATA)
            for i in range(MAX_CONTENT_LINES + 10)
            if filter_kw in '{0}Some'.format(i)
        ]
    )

    shutil.rmtree(temp_dir)
