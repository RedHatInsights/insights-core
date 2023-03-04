import os
import pytest
import tempfile

from insights.core import dr
from insights.core.context import HostContext
from insights.core.spec_factory import listdir


@pytest.fixture
def sample_directory(scope="module"):
    tmpdir = tempfile.mkdtemp()
    os.mkdir(tmpdir + "/dir1")
    os.mkdir(tmpdir + "/dir2")
    for d in ["dir1", "dir2"]:
        for f in ["file_a", "file_b"]:
            fd = open(tmpdir + "/" + d + "/" + f, "w")
            fd.close()
    yield tmpdir
    for d in ["dir1", "dir2"]:
        for f in ["file_a", "file_b"]:
            os.remove(tmpdir + "/" + d + "/" + f)
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


CASES_PATH_FORMAT = [
    # default path_format, directory
    (listdir("dir1/"), ["file_a", "file_b"]),
    # default path_format, glob
    (listdir("*/*"), ["file_a", "file_b", "file_a", "file_b"]),
]


CASES_IGNORE = [
    # ignore filter works on basenames when listing a directory
    (listdir("dir1", ignore=".*a"), ["file_b"]),
    # ignore filter works ONLY on basenames paths when listing a directory (nothing is filtered out)
    (listdir("dir1", ignore="dir1.*"), ["file_a", "file_b"]),
    # ignore filter works on relative paths when matching a glob (keeps only files from dir2)
    (listdir("*/*", ignore="dir1.*"), ["file_a", "file_b"]),
    # ignore filter does not cause ContentException when listing a directory
    (listdir("dir1", ignore="file"), []),
    # ignore filter does not cause ContentException when matching a glob
    (listdir("*/*", ignore="dir"), []),
]


@pytest.mark.parametrize(
    "spec,result", CASES_PATH_FORMAT + CASES_IGNORE
)
def test_non_empty_results(sample_directory, spec, result):
    broker = run_listdir_test(sample_directory, spec)
    assert broker[spec] == result


def test_ignore_uses_absolute_path_with_glob(sample_directory):
    spec = listdir("*/*", ignore=sample_directory)
    broker = run_listdir_test(sample_directory, spec)
    assert broker[spec] == []


@pytest.mark.parametrize(
    "spec",
    [
        listdir("nothing/there"),
        listdir("nothing/there/*"),
    ]
)
def test_nothing_found(sample_directory, spec):
    broker = run_listdir_test(sample_directory, spec)
    assert spec not in broker
