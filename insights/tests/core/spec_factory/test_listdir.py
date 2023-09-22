import os
import pytest
import tempfile

from insights.core import dr
from insights.core.context import HostContext
from insights.core.exceptions import ContentException
from insights.core.spec_factory import listdir


@pytest.fixture
def sample_directory(scope="module"):
    def touch(fpath):
        fd = open(fpath, "w")
        fd.close()

    # Python2 does not have tempfile.TemporaryDirectory
    tmpdir = tempfile.mkdtemp()
    os.mkdir(tmpdir + "/dir1")
    os.mkdir(tmpdir + "/dir2")
    touch(tmpdir + "/dir1/file_a")
    touch(tmpdir + "/dir1/file_b")
    yield tmpdir
    os.remove(tmpdir + "/dir1/file_a")
    os.remove(tmpdir + "/dir1/file_b")
    os.rmdir(tmpdir + "/dir1")
    os.rmdir(tmpdir + "/dir2")
    os.rmdir(tmpdir)


def run_listdir_test(sample_directory, spec):
    ctx = HostContext()
    ctx.root = sample_directory
    broker = dr.Broker()
    broker[HostContext] = ctx
    broker = dr.run([spec], broker)
    return broker


CASES_RETURNS_LIST = [
    # directory with files, no filter
    (listdir("dir1/"), ["file_a", "file_b"]),
    # empty directory, no filter
    (listdir("dir2/"), []),
    # ignore filter works on basenames
    (listdir("dir1", ignore=".*a"), ["file_b"]),
    # ignore filter works ONLY on basenames (nothing is filtered out here)
    (listdir("dir1", ignore="dir1.*"), ["file_a", "file_b"]),
    # empty list is returned when the ignore filter matches all basenames
    (listdir("dir1", ignore="file"), []),
]


@pytest.mark.parametrize(
    "spec,result", CASES_RETURNS_LIST
)
def test_returns_list(sample_directory, spec, result):
    broker = run_listdir_test(sample_directory, spec)
    assert broker[spec] == result


@pytest.mark.parametrize(
    "spec",
    [
        # directory does not exist
        listdir("nothing/there"),
        # path is not a directory
        listdir("dir1/file_a"),
    ]
)
def test_raises_content_exception(sample_directory, spec):
    broker = run_listdir_test(sample_directory, spec)
    assert spec not in broker
    # PluginType masks ContentException as a new SkipComponent even though
    # ContentException is a SkipComponet instance; it is not possible to test
    # that a component raises ContentException using the broker even with
    # broker.store_skips == True
    with pytest.raises(ContentException):
        spec(broker)
