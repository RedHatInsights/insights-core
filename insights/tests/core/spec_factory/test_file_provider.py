import os
import os.path
import pytest

from insights.core.spec_factory import FileProvider


@pytest.fixture(scope="module")
def sample_file(tmpdir_factory):
    # str() required for Python 2.7
    root = str(tmpdir_factory.mktemp("test_file_provider"))
    relpath = "sample_file.txt"
    abspath = os.path.join(root, relpath)
    fd = open(abspath, "w")
    fd.close()
    return root, relpath


class DummyFileProvider(FileProvider):
    def load():
        return ""


def test_repr(sample_file):
    root, relpath = sample_file
    provider = DummyFileProvider(relpath, root=root)
    # example: DummyFileProvider('/tmp/pytest0/test_file_provider/sample_file.txt')
    assert repr(provider) == "DummyFileProvider('%s/%s')" % (root, relpath)
