import os
import pytest

from insights.core import dr
from insights.core.context import HostContext
from insights.core.spec_factory import listglob


@pytest.fixture(scope="module")
def sample_directory(tmpdir_factory):
    def touch(fpath):
        fd = open(fpath, "w")
        fd.close()

    tmpdir = str(tmpdir_factory.mktemp("test_listglob"))
    os.mkdir(tmpdir + "/dir1")
    os.mkdir(tmpdir + "/dir2")
    for d in ["dir1", "dir2"]:
        for f in ["file_a", "file_b"]:
            touch(tmpdir + "/" + d + "/" + f)
    return tmpdir


def run_listglob_test(sample_directory, spec):
    ctx = HostContext()
    ctx.root = sample_directory
    broker = dr.Broker()
    broker[HostContext] = ctx
    broker = dr.run([spec], broker)
    return broker


@pytest.mark.parametrize(
    "spec,result",
    [
        # return empty list if nothing matches
        (listglob("nothing/there"), []),
        (listglob("nothing/there/*"), []),
        (listglob("dir1/*", ignore="file"), []),
        # matching starts at the execution context root
        (listglob("*"), ["dir1", "dir2"]),
        # a more complex glob
        (listglob("*/*"), ["dir1/file_a", "dir1/file_b", "dir2/file_a", "dir2/file_b"]),
        # ignore filter works on paths relative to the execution context root
        (listglob("*/*", ignore="dir1.*"), ["dir2/file_a", "dir2/file_b"]),
    ]
)
def test_match_results(sample_directory, spec, result):
    broker = run_listglob_test(sample_directory, spec)
    assert broker[spec] == result


def test_ignore_does_not_use_absolute_paths(sample_directory):
    spec = listglob("dir1/file_a", ignore=sample_directory)
    broker = run_listglob_test(sample_directory, spec)
    assert broker[spec] == ["dir1/file_a"]
